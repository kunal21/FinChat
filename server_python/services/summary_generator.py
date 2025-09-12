from typing import Dict, Any, List
from datetime import datetime, date
from db import db
from models import Transaction, TransactionView
from sqlalchemy import func, and_, extract
from services.vector_store import VectorStore
from openai_client import openai_client
import logging

logger = logging.getLogger(__name__)

def create_tx_summary(transaction: Transaction) -> str:
    """Create a natural language summary for a single transaction."""
    amount = abs(float(transaction.amount))
    category = transaction.personal_finance_category_primary or "Unknown"
    return f"{transaction.name} on {transaction.date} for ${amount:.2f} in {category}"

def create_monthly_category_summary(user_id: str, category: str, year: int, month: int) -> str:
    """Create a monthly category summary by querying the database."""
    # Query transactions for this user, category, and month
    transactions = db.session.query(TransactionView).filter(
        and_(
            TransactionView.user_id == user_id,
            TransactionView.personal_finance_category_primary == category,
            extract('year', TransactionView.date) == year,
            extract('month', TransactionView.date) == month
        )
    ).all()
    
    if not transactions:
        return f"{year}-{month:02d} {category}: No transactions"
    
    total = sum(abs(float(tx.amount)) for tx in transactions)
    
    # Group by merchant/name
    merchants = {}
    for tx in transactions:
        merchants[tx.name] = merchants.get(tx.name, 0) + abs(float(tx.amount))
    
    # Top 3 merchants
    top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:3]
    merchant_str = ", ".join([f"{name} (${amt:.2f})" for name, amt in top_merchants])
    
    return f"{year}-{month:02d} {category}: ${total:.2f} total, top merchants: {merchant_str}"

async def index_transaction_summaries(plaid_item_id: str, added_transactions: List[Dict], modified_transactions: List[Dict]) -> None:
    """Index transaction summaries to Qdrant after webhook processing."""
    try:
        # Get user_id from the item
        from db.queries import retrieve_item_by_plaid_item_id
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        user_id = str(item['user_id'])
        
        vector_store = VectorStore()
        
        # Process added transactions
        for tx_data in added_transactions:
            # Get the saved transaction from DB
            tx = Transaction.query.filter_by(plaid_transaction_id=tx_data['transaction_id']).first()
            if not tx:
                continue
                
            summary_text = create_tx_summary(tx)
            embedding = openai_client.embed_texts([summary_text])[0]
            
            # Use plaid_transaction_id as stable point_id
            point_id = f"tx_{tx_data['transaction_id']}"
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
                    "tx_id": tx_data['transaction_id']
                }
            )
        
        # Process modified transactions (same as added)
        for tx_data in modified_transactions:
            tx = Transaction.query.filter_by(plaid_transaction_id=tx_data['transaction_id']).first()
            if not tx:
                continue
                
            summary_text = create_tx_summary(tx)
            embedding = openai_client.embed_texts([summary_text])[0]
            
            point_id = f"tx_{tx_data['transaction_id']}"
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
                    "tx_id": tx_data['transaction_id']
                }
            )
            
        logger.info(f"Indexed {len(added_transactions) + len(modified_transactions)} transaction summaries for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error indexing transaction summaries: {e}")

async def create_monthly_rollups(user_id: str) -> None:
    """Create monthly category rollups for a user (can be called periodically)."""
    try:
        # Get all categories for this user from the last 3 months
        from datetime import datetime, timedelta
        three_months_ago = datetime.now() - timedelta(days=90)
        
        categories = db.session.query(TransactionView.personal_finance_category_primary).filter(
            and_(
                TransactionView.user_id == user_id,
                TransactionView.date >= three_months_ago,
                TransactionView.personal_finance_category_primary.isnot(None)
            )
        ).distinct().all()
        
        vector_store = VectorStore()
        
        for (category,) in categories:
            if not category:
                continue
                
            # Get current month and previous month
            now = datetime.now()
            for year, month in [(now.year, now.month), (now.year, now.month - 1) if now.month > 1 else (now.year - 1, 12)]:
                summary_text = create_monthly_category_summary(user_id, category, year, month)
                embedding = openai_client.embed_texts([summary_text])[0]
                
                point_id = f"monthly_{user_id}_{year}_{month:02d}_{category.replace(' ', '_')}"
                vector_store.upsert_tx_summary(
                    point_id=point_id,
                    user_id=user_id,
                    vector=embedding,
                    text=summary_text,
                    summary_type="category_month",
                    extra={
                        "period": f"{year}-{month:02d}",
                        "category_primary": category,
                        "amount": float(sum(abs(float(tx.amount)) for tx in db.session.query(TransactionView).filter(
                            and_(
                                TransactionView.user_id == user_id,
                                TransactionView.personal_finance_category_primary == category,
                                extract('year', TransactionView.date) == year,
                                extract('month', TransactionView.date) == month
                            )
                        ).all()))
                    }
                )
                
        logger.info(f"Created monthly rollups for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error creating monthly rollups: {e}")