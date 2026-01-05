from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

# Add server_python to Python path so imports work correctly
# This allows the script to be run from anywhere
server_python_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(server_python_dir))

from dotenv import load_dotenv
from sqlalchemy import distinct
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from db import db
from models.account import Account
from models.article import Article
from models.holding import Holding
from models.item import Item
from models.user import User
from models.user_impact import UserImpact
from news_ingestion.pipeline import article_exists_by_canonical_url, insert_deadletter
from news_ingestion.util import article_id_from, build_clean_text, canonicalize_url, sha256_text
from portfolio_impact.clients.finnhub_client import finnhub_fetch, parse_finnhub_article
from portfolio_impact.analyzers.impact_analyzer import analyze_impact_with_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_all_user_tickers(db_session) -> List[str]:
    """
    Get all unique ticker symbols from user holdings.

    Joins: Holding -> Account -> Item
    Filters: ticker_symbol is not null and not empty

    Returns:
        List of uppercase ticker symbols
    """
    tickers = (
        db_session.query(distinct(Holding.ticker_symbol))
        .join(Account, Holding.account_id == Account.id)
        .join(Item, Account.item_id == Item.id)
        .filter(Holding.ticker_symbol.isnot(None))
        .filter(Holding.ticker_symbol != '')
        .all()
    )
    return [ticker[0].upper() for ticker in tickers if ticker[0]]


def get_users_holding_ticker(db_session, ticker: str) -> List[int]:
    """
    Get user IDs for all users who hold a specific ticker.

    Joins: User -> Item -> Account -> Holding
    Filters: ticker_symbol matches (case-insensitive)

    Returns:
        List of user IDs
    """
    user_ids = (
        db_session.query(distinct(User.id))
        .join(Item, User.id == Item.user_id)
        .join(Account, Item.id == Account.item_id)
        .join(Holding, Account.id == Holding.account_id)
        .filter(db.func.upper(Holding.ticker_symbol) == ticker.upper())
        .all()
    )
    return [user_id[0] for user_id in user_ids]


def insert_article_with_ticker(db_session, article_data: Dict) -> str:
    """
    Insert article into database.

    Args:
        article_data: Dict with url, title, published_at, ticker, etc.

    Returns:
        article_id (SHA256 hash)
    """
    canonical = canonicalize_url(article_data["url"])
    article_id = article_id_from(
        canonical,
        article_data.get("title") or "",
        article_data["published_at"].isoformat()
    )

    article = Article(
        id=article_id,
        ticker=article_data.get("ticker"),
        title=article_data.get("title"),
        summary=article_data.get("description"),
        url=article_data["url"],
        canonical_url=canonical,
        source=article_data.get("source"),
        published_at=article_data["published_at"],
        raw_storage_key=None,  # Not storing raw Finnhub responses
        processed=False
    )

    db_session.add(article)
    db_session.commit()
    return article_id


def insert_user_impact(db_session, impact_data: Dict) -> None:
    """
    Insert UserImpact record.

    Args:
        impact_data: Dict with user_id, article_id, ticker, impact_level, etc.
    """
    impact_id = sha256_text(
        f"{impact_data['user_id']}\n{impact_data['article_id']}\n{impact_data['ticker']}"
    )

    impact = UserImpact(
        id=impact_id,
        user_id=impact_data["user_id"],
        article_id=impact_data["article_id"],
        ticker=impact_data["ticker"],
        impact_level=impact_data["impact_level"],
        impact_summary=impact_data["impact_summary"],
        estimated_effect=impact_data.get("estimated_effect"),
        read=False,
        dismissed=False
    )

    db_session.add(impact)
    db_session.commit()


def process_ticker(
    ticker: str,
    from_date: str,
    to_date: str,
    finnhub_api_key: str,
    openai_api_key: str,
    llm_model: str,
    db_session,
    metrics: Dict
) -> None:
    """Process news articles for a single ticker."""

    logger.info(f"Processing ticker: {ticker}")

    # 1. Fetch news from Finnhub
    try:
        raw_articles = finnhub_fetch(finnhub_api_key, ticker, from_date, to_date)
        logger.info(f"  Fetched {len(raw_articles)} articles for {ticker}")
        metrics["articles_fetched"] += len(raw_articles)
    except Exception as exc:
        logger.error(f"  Failed to fetch news for {ticker}: {exc}")
        raise

    # 2. Process each article
    for raw_article in raw_articles:
        try:
            # Parse article
            parsed = parse_finnhub_article(raw_article, ticker)

            # Validate required fields
            if not parsed.get("url") or not parsed.get("published_at"):
                logger.debug(f"  Skipping article (missing url or published_at)")
                metrics["articles_skipped"] += 1
                continue

            # Check for duplicates
            canonical = canonicalize_url(parsed["url"])
            if article_exists_by_canonical_url(db_session, canonical):
                logger.debug(f"  Article already exists: {canonical}")
                metrics["articles_skipped"] += 1
                continue

            # Insert article
            article_id = insert_article_with_ticker(db_session, parsed)
            title_preview = (parsed.get('title') or '')[:50]
            logger.info(f"  Inserted article: {article_id} ({title_preview}...)")
            metrics["articles_inserted"] += 1

            # Analyze materiality
            try:
                clean_text = build_clean_text(
                    parsed.get("title"),
                    parsed.get("description"),
                    parsed.get("content")
                )

                impact_analysis = analyze_impact_with_retry(
                    clean_text=clean_text,
                    ticker=ticker,
                    api_key=openai_api_key,
                    model=llm_model
                )

                metrics["articles_analyzed"] += 1

                # Update article with analysis results
                article = db_session.query(Article).filter(Article.id == article_id).first()
                article.is_material = impact_analysis["is_material"]
                article.structured_data = impact_analysis
                article.processed = True
                db_session.commit()

                # If material, create UserImpact records
                if impact_analysis["is_material"]:
                    metrics["material_articles"] += 1
                    user_ids = get_users_holding_ticker(db_session, ticker)
                    logger.info(f"  Material article affects {len(user_ids)} users")

                    for user_id in user_ids:
                        try:
                            insert_user_impact(db_session, {
                                "user_id": user_id,
                                "article_id": article_id,
                                "ticker": ticker,
                                "impact_level": impact_analysis["impact_level"],
                                "impact_summary": impact_analysis["impact_summary"],
                                "estimated_effect": impact_analysis.get("estimated_effect")
                            })
                            metrics["impacts_created"] += 1
                        except SQLAlchemyError as exc:
                            logger.error(f"  Failed to insert UserImpact for user {user_id}: {exc}")
                            db_session.rollback()

            except Exception as exc:
                logger.error(f"  Failed to analyze article {article_id}: {exc}")
                db_session.rollback()

                # Insert into dead letter queue
                try:
                    insert_deadletter(db_session, {
                        "id": sha256_text(f"{article_id}\nimpact_analysis\n{str(exc)}"),
                        "stage": "impact_analysis",
                        "url": parsed["url"],
                        "error": str(exc),
                        "payload_json": {
                            "article_id": article_id,
                            "ticker": ticker
                        }
                    })
                except SQLAlchemyError:
                    db_session.rollback()

                metrics["errors"] += 1

        except Exception as exc:
            logger.error(f"  Error processing article for {ticker}: {exc}")
            metrics["errors"] += 1


def main() -> None:
    """Main batch job entry point."""

    # 1. Load configuration
    load_dotenv()
    finnhub_api_key = os.environ.get("FINNHUB_API_KEY")
    openai_api_key = os.environ.get("OPENAI_CLIENT_ID")
    llm_model = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    if not finnhub_api_key:
        logger.error("FINNHUB_API_KEY not found in environment")
        return
    if not openai_api_key:
        logger.error("OPENAI_CLIENT_ID not found in environment")
        return

    logger.info("Starting Finnhub news ingestion batch job")

    # 2. Initialize Flask app context
    app = create_app()

    # 3. Initialize metrics
    metrics = {
        "tickers_processed": 0,
        "articles_fetched": 0,
        "articles_inserted": 0,
        "articles_skipped": 0,
        "articles_analyzed": 0,
        "material_articles": 0,
        "impacts_created": 0,
        "errors": 0
    }

    with app.app_context():
        try:
            # 4. Get all unique tickers from holdings
            tickers = get_all_user_tickers(db.session)
            logger.info(f"Found {len(tickers)} unique tickers in holdings")

            if not tickers:
                logger.warning("No tickers found in holdings table")
                return

            # 5. Calculate date range (last 24 hours)
            to_date = datetime.now(timezone.utc)
            from_date = to_date - timedelta(days=1)
            from_str = from_date.strftime("%Y-%m-%d")
            to_str = to_date.strftime("%Y-%m-%d")

            # 6. Process each ticker
            for ticker in tickers:
                try:
                    process_ticker(
                        ticker=ticker,
                        from_date=from_str,
                        to_date=to_str,
                        finnhub_api_key=finnhub_api_key,
                        openai_api_key=openai_api_key,
                        llm_model=llm_model,
                        db_session=db.session,
                        metrics=metrics
                    )
                    metrics["tickers_processed"] += 1
                except Exception as exc:
                    logger.error(f"Error processing ticker {ticker}: {exc}")
                    metrics["errors"] += 1

            # 7. Log final metrics
            logger.info("Batch job completed successfully")
            logger.info(f"Metrics: {metrics}")

        except Exception as exc:
            logger.error(f"Fatal error in batch job: {exc}")
            raise


if __name__ == "__main__":
    main()
