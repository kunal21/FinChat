#!/usr/bin/env python3
"""
Backfill existing data into Qdrant for RAG.
Run this once after setting up Qdrant to populate it with historical data.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import db
from models import Message, Transaction, User, TransactionView
from services.vector_store import VectorStore
from services.summary_generator import create_tx_summary, create_monthly_category_summary
from openai_client import openai_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def backfill_messages():
    """Index all existing messages into Qdrant."""
    logger.info("Starting message backfill...")
    
    vector_store = VectorStore()
    messages = Message.query.order_by(Message.created_at).all()
    
    for msg in messages:
        try:
            embedding = openai_client.embed_texts([msg.text])[0]
            vector_store.upsert_message(
                point_id=msg.id,
                user_id=str(msg.user_id),
                vector=embedding,
                text=msg.text,
                author=msg.author,
                extra={
                    "message_id": msg.id,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
            )
            logger.info(f"Indexed message {msg.id} for user {msg.user_id}")
        except Exception as e:
            logger.error(f"Failed to index message {msg.id}: {e}")
    
    logger.info(f"Completed message backfill: {len(messages)} messages")

async def backfill_transactions():
    """Index all existing transactions into Qdrant."""
    logger.info("Starting transaction backfill...")
    
    vector_store = VectorStore()
    transactions = Transaction.query.order_by(Transaction.date).all()
    
    for tx in transactions:
        try:
            # Get user_id from the transaction's account
            user_id = str(tx.account.user_id)
            
            summary_text = create_tx_summary(tx)
            embedding = openai_client.embed_texts([summary_text])[0]
            
            point_id = f"tx_{tx.plaid_transaction_id}"
            vector_store.upsert_tx_summary(
                point_id=point_id,
                user_id=user_id,
                vector=embedding,
                text=summary_text,
                summary_type="transaction",
                extra={
                    "date": tx.date.isoformat(),
                    "amount": float(tx.amount),
                    "category_primary": tx.personal_finance_category_primary,
                    "category_detailed": tx.personal_finance_category_detailed,
                    "merchant": tx.name,
                    "tx_id": tx.plaid_transaction_id
                }
            )
            logger.info(f"Indexed transaction {tx.plaid_transaction_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to index transaction {tx.plaid_transaction_id}: {e}")
    
    logger.info(f"Completed transaction backfill: {len(transactions)} transactions")

async def backfill_monthly_rollups():
    """Create monthly category rollups for all users."""
    logger.info("Starting monthly rollups backfill...")
    
    users = User.query.all()
    vector_store = VectorStore()
    
    for user in users:
        try:
            # Get all categories for this user from the last 6 months
            six_months_ago = datetime.now() - timedelta(days=180)
            
            categories = db.session.query(TransactionView.personal_finance_category_primary).filter(
                TransactionView.user_id == user.id,
                TransactionView.date >= six_months_ago,
                TransactionView.personal_finance_category_primary.isnot(None)
            ).distinct().all()
            
            for (category,) in categories:
                if not category:
                    continue
                
                # Create rollups for the last 6 months
                for i in range(6):
                    target_date = datetime.now() - timedelta(days=30*i)
                    year, month = target_date.year, target_date.month
                    
                    summary_text = create_monthly_category_summary(user.id, category, year, month)
                    if "No transactions" in summary_text:
                        continue
                        
                    embedding = openai_client.embed_texts([summary_text])[0]
                    
                    point_id = f"monthly_{user.id}_{year}_{month:02d}_{category.replace(' ', '_')}"
                    vector_store.upsert_tx_summary(
                        point_id=point_id,
                        user_id=str(user.id),
                        vector=embedding,
                        text=summary_text,
                        summary_type="category_month",
                        extra={
                            "period": f"{year}-{month:02d}",
                            "category_primary": category
                        }
                    )
                    
            logger.info(f"Created monthly rollups for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to create rollups for user {user.id}: {e}")
    
    logger.info("Completed monthly rollups backfill")

async def main():
    """Run all backfill operations."""
    logger.info("Starting Qdrant backfill...")
    
    try:
        await backfill_messages()
        await backfill_transactions()
        await backfill_monthly_rollups()
        logger.info("Backfill completed successfully!")
    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())