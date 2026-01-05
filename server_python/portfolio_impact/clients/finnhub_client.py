from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import requests


def _parse_datetime_from_unix(timestamp: int) -> datetime:
    """Convert Unix timestamp to datetime object with UTC timezone."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def finnhub_fetch(api_key: str, ticker: str, from_date: str, to_date: str) -> List[Dict]:
    """
    Fetch news articles from Finnhub API for a specific ticker.

    Args:
        api_key: Finnhub API key
        ticker: Stock ticker symbol (e.g., "AAPL")
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format

    Returns:
        List of article dictionaries from Finnhub API

    Raises:
        requests.HTTPError: If API request fails
    """
    params = {
        "symbol": ticker.upper(),
        "from": from_date,
        "to": to_date,
        "token": api_key
    }

    response = requests.get(
        "https://finnhub.io/api/v1/company-news",
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def parse_finnhub_article(article: Dict, ticker: str) -> Dict:
    """
    Parse Finnhub article into normalized format compatible with Article model.

    Args:
        article: Raw article dict from Finnhub API with keys:
                 - datetime: Unix timestamp
                 - headline: Article title
                 - summary: Article description/content
                 - url: Article URL
                 - source: News source
        ticker: Ticker symbol to associate with article

    Returns:
        Normalized article dict with keys:
        - url, source, title, description, content, published_at, ticker
    """
    published_at = None
    if article.get("datetime"):
        published_at = _parse_datetime_from_unix(article["datetime"])

    return {
        "url": article.get("url", ""),
        "source": article.get("source"),
        "title": article.get("headline"),
        "description": article.get("summary"),
        "content": article.get("summary"),  # Finnhub provides summary, not full content
        "published_at": published_at,
        "ticker": ticker.upper()
    }
