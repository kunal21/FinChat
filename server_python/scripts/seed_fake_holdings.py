#!/usr/bin/env python3
"""
Seed fake holdings data for testing portfolio impact news ingestion.

This script creates realistic investment holdings for popular stocks that are
likely to have recent news coverage from Finnhub.

Usage:
    docker compose exec server python scripts/seed_fake_holdings.py
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import List

# Add server_python to Python path
server_python_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(server_python_dir))

from app import create_app
from db import db
from models.account import Account
from models.holding import Holding
from models.item import Item
from models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Popular stocks with frequent news coverage
POPULAR_HOLDINGS = [
    {
        "ticker_symbol": "AAPL",
        "name": "Apple Inc.",
        "security_type": "equity",
        "quantity": 50,
        "institution_price": 195.50,
    },
    {
        "ticker_symbol": "MSFT",
        "name": "Microsoft Corporation",
        "security_type": "equity",
        "quantity": 30,
        "institution_price": 425.75,
    },
    {
        "ticker_symbol": "GOOGL",
        "name": "Alphabet Inc. Class A",
        "security_type": "equity",
        "quantity": 25,
        "institution_price": 175.25,
    },
    {
        "ticker_symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "security_type": "equity",
        "quantity": 40,
        "institution_price": 220.80,
    },
    {
        "ticker_symbol": "TSLA",
        "name": "Tesla, Inc.",
        "security_type": "equity",
        "quantity": 20,
        "institution_price": 380.00,
    },
    {
        "ticker_symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "security_type": "equity",
        "quantity": 15,
        "institution_price": 875.00,
    },
    {
        "ticker_symbol": "META",
        "name": "Meta Platforms, Inc.",
        "security_type": "equity",
        "quantity": 35,
        "institution_price": 550.25,
    },
    {
        "ticker_symbol": "JPM",
        "name": "JPMorgan Chase & Co.",
        "security_type": "equity",
        "quantity": 45,
        "institution_price": 210.50,
    },
    {
        "ticker_symbol": "V",
        "name": "Visa Inc.",
        "security_type": "equity",
        "quantity": 25,
        "institution_price": 305.75,
    },
    {
        "ticker_symbol": "WMT",
        "name": "Walmart Inc.",
        "security_type": "equity",
        "quantity": 30,
        "institution_price": 92.40,
    },
]


def get_or_create_investment_account(user_id: int) -> Account:
    """Get existing investment account or create one if it doesn't exist."""

    # Find user's item
    item = Item.query.filter_by(user_id=user_id).first()
    if not item:
        logger.error(f"No Plaid item found for user {user_id}")
        raise ValueError(f"User {user_id} must have a linked Plaid item")

    # Look for existing investment account
    investment_account = (
        Account.query
        .filter_by(item_id=item.id, type="investment")
        .first()
    )

    if investment_account:
        logger.info(f"Found existing investment account: {investment_account.name}")
        return investment_account

    # Create new investment account
    logger.info("Creating new investment account")
    new_account = Account(
        item_id=item.id,
        plaid_account_id=f"fake_investment_account_{user_id}",
        name="Test Investment Account",
        mask="0000",
        official_name="Test Brokerage Account",
        current_balance=Decimal("0"),
        available_balance=Decimal("0"),
        iso_currency_code="USD",
        type="investment",
        subtype="brokerage",
    )
    db.session.add(new_account)
    db.session.commit()

    return new_account


def create_fake_holdings(account_id: int, holdings_data: List[dict]) -> int:
    """Create fake holdings for an account."""

    logger.info(f"Clearing existing holdings for account {account_id}")
    Holding.query.filter_by(account_id=account_id).delete()

    count = 0
    now = datetime.now(timezone.utc)

    for holding_data in holdings_data:
        quantity = Decimal(str(holding_data["quantity"]))
        price = Decimal(str(holding_data["institution_price"]))
        value = quantity * price

        holding = Holding(
            account_id=account_id,
            plaid_account_id=f"fake_account_{account_id}",
            security_id=f"fake_security_{holding_data['ticker_symbol']}",
            name=holding_data["name"],
            ticker_symbol=holding_data["ticker_symbol"],
            security_type=holding_data["security_type"],
            quantity=quantity,
            institution_price=price,
            institution_price_as_of=now,
            institution_value=value,
            cost_basis=value * Decimal("0.85"),  # Assume 15% gain
            iso_currency_code="USD",
        )
        db.session.add(holding)
        count += 1

        logger.info(
            f"  + {holding_data['ticker_symbol']}: {quantity} shares @ ${price} = ${value}"
        )

    db.session.commit()
    return count


def main():
    """Main entry point."""
    logger.info("Starting fake holdings seed script")

    app = create_app()
    with app.app_context():
        # Get all users
        users = User.query.all()
        if not users:
            logger.error("No users found in database. Please create a user first.")
            return 1

        logger.info(f"Found {len(users)} user(s)")

        for user in users:
            logger.info(f"\nProcessing user: {user.username} (ID: {user.id})")

            try:
                # Get or create investment account
                account = get_or_create_investment_account(user.id)

                # Create fake holdings
                count = create_fake_holdings(account.id, POPULAR_HOLDINGS)

                logger.info(f"✓ Created {count} holdings for {user.username}")

            except ValueError as e:
                logger.error(f"✗ Skipping user {user.username}: {e}")
                continue
            except Exception as e:
                logger.exception(f"✗ Error processing user {user.username}: {e}")
                db.session.rollback()
                continue

        # Summary
        logger.info("\n" + "="*60)
        total_holdings = Holding.query.count()
        logger.info(f"Total holdings in database: {total_holdings}")

        # Show holdings by ticker
        from sqlalchemy import func
        ticker_counts = (
            db.session.query(
                Holding.ticker_symbol,
                func.count(Holding.id).label("count")
            )
            .group_by(Holding.ticker_symbol)
            .all()
        )

        logger.info("\nHoldings by ticker:")
        for ticker, count in ticker_counts:
            logger.info(f"  {ticker}: {count} user(s)")

        logger.info("\nFake holdings seeded successfully!")
        logger.info("You can now run: docker compose exec server python portfolio_impact/jobs/batch_job.py")

        return 0


if __name__ == "__main__":
    sys.exit(main())
