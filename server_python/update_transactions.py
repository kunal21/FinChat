"""
Functions for updating transactions from Plaid.
"""

import os
from typing import Dict, Any
from plaid_client import plaid_client
from db import db
from db.queries import retrieve_item_by_plaid_item_id
from models import Transaction, Item, Account
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from services.summary_generator import index_transaction_summaries, create_monthly_rollups
import logging
logger = logging.getLogger(__name__)

async def update_transactions(plaid_item_id: str) -> Dict[str, int]:
    """
    Update transactions for a given Plaid item ID.

    Args:
        plaid_item_id: The Plaid item ID to update transactions for

    Returns:
        A dictionary containing counts of added, modified, and removed transactions
    """
    # Get the item's access token
    item = await retrieve_item_by_plaid_item_id(plaid_item_id)
    access_token = item['access_token']

    # Get the latest cursor
    cursor = await get_latest_cursor(plaid_item_id)
    if cursor is None:
        cursor = ""

    added = []
    modified = []
    removed = [] # Removed transaction ids
    has_more = True
    while has_more:
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=str(cursor),
        )
        try:
            response = plaid_client.client.transactions_sync(request)

            # Add debug logging
            print(f"DEBUG: Plaid response - added: {len(response['added'])}, modified: {len(response['modified'])}, removed: {len(response['removed'])}")
            print(f"DEBUG: Has more: {response['has_more']}")
            print(f"DEBUG: Next cursor: {response['next_cursor']}")
            if response['added']:
                print(f"DEBUG: First added transaction: {response['added'][0]}")
            
            # Add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])

            has_more = response['has_more']

            # Update cursor to the next cursor
            cursor = response['next_cursor']
        except Exception as e:
            logger.error(f"Error syncing transactions: {e, cursor}")
            raise

    # Fetch accounts from Plaid API
    try:
        request = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.client.accounts_get(request)
        accounts = accounts_response['accounts']
        await update_accounts_in_db(plaid_item_id, accounts)
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise
    
    # Update the database with new transactions
    await update_transactions_in_db(
        plaid_item_id,
        added,
        modified,
        removed
    )

    # Index transaction summaries to Qdrant
    try:
        await index_transaction_summaries(plaid_item_id, added, modified)
        
        # Create monthly rollups for this user
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        await create_monthly_rollups(str(item['user_id']))
    except Exception as e:
        logger.warning(f"Qdrant indexing failed for transactions: {e}")
    
    # Update the cursor
    await update_cursor(plaid_item_id, cursor)

    return {
        'added_count': len(added),
        'modified_count': len(modified),
        'removed_count': len(removed)
    }

async def get_latest_cursor(plaid_item_id: str) -> str:
    """
    Get the latest cursor for a Plaid item.

    Args:
        plaid_item_id: The Plaid item ID

    Returns:
        The latest cursor value
    """
    item = Item.query.filter_by(plaid_item_id=plaid_item_id).first()
    return item.transactions_cursor if item else None

async def update_cursor(plaid_item_id: str, cursor: str) -> None:
    """
    Update the cursor for a Plaid item.

    Args:
        plaid_item_id: The Plaid item ID
        cursor: The new cursor value
    """
    item = Item.query.filter_by(plaid_item_id=plaid_item_id).first()
    if item:
        item.transactions_cursor = cursor
        db.session.commit()

async def update_transactions_in_db(
    plaid_item_id: str,
    added: list,
    modified: list,
    removed: list
) -> None:
    """
    Update transactions in the database.

    Args:
        plaid_item_id: The Plaid item ID
        added: List of new transactions
        modified: List of modified transactions
        removed: List of removed transaction IDs
    """
    try:
         # Insert new transactions
        for transaction in added:
            account = Account.query.filter_by(plaid_account_id=transaction['account_id']).first()
            if not account:
                logger.warning(f"Account with plaid_account_id {transaction['account_id']} not found.")
                continue
            
            # Check if transaction already exists
            existing_transaction = Transaction.query.filter_by(
                plaid_transaction_id=transaction['transaction_id']
            ).first()
            
            if existing_transaction:
                logger.info(f"Transaction {transaction['transaction_id']} already exists, skipping")
                continue
            
            new_transaction = Transaction(
                plaid_transaction_id=transaction['transaction_id'],
                account_id=account.id,
                plaid_category_id=transaction.get('category_id'),
                category=transaction.get('category'),
                personal_finance_category_primary=transaction.get('personal_finance_category', {}).get('primary'),
                personal_finance_category_detailed=transaction.get('personal_finance_category', {}).get('detailed'),
                type=transaction.get('transaction_type'),
                name=transaction['name'],
                amount=transaction['amount'],
                iso_currency_code=transaction.get('iso_currency_code'),
                unofficial_currency_code=transaction.get('unofficial_currency_code'),
                date=transaction['date'],
                pending=transaction['pending'],
                account_owner=transaction.get('account_owner')
            )
            db.session.add(new_transaction)
            print(f"DEBUG: Added transaction {transaction['transaction_id']} to session")

        # Update modified transactions
        for transaction in modified:
            existing_transaction = Transaction.query.filter_by(
                plaid_transaction_id=transaction['transaction_id']
            ).first()
            if existing_transaction:
                account = Account.query.filter_by(plaid_account_id=transaction['account_id']).first()
                if not account:
                    logger.warning(f"Account with plaid_account_id {transaction['account_id']} not found when updating tx {transaction.get('transaction_id')}")
                    continue
                existing_transaction.account_id = account.id  # Update account_id
                existing_transaction.plaid_category_id = transaction.get('category_id')
                existing_transaction.category = transaction.get('category')
                # defensive accessors for personal finance category
                pfc = transaction.get('personal_finance_category') or {}
                existing_transaction.personal_finance_category_primary = pfc.get('primary')
                existing_transaction.personal_finance_category_detailed = pfc.get('detailed')
                existing_transaction.type = transaction.get('transaction_type')
                existing_transaction.name = transaction.get('name')
                existing_transaction.amount = transaction.get('amount')
                existing_transaction.iso_currency_code = transaction.get('iso_currency_code')
                existing_transaction.unofficial_currency_code = transaction.get('unofficial_currency_code')
                existing_transaction.date = transaction.get('date')
                existing_transaction.pending = transaction.get('pending')
                existing_transaction.account_owner = transaction.get('account_owner')

        # Remove deleted transactions
        for transaction_id in removed:
            # Delete from Qdrant first
            try:
                from services.vector_store import VectorStore
                vector_store = VectorStore()
                point_id = f"tx_{transaction_id}"
                vector_store.client.delete(
                    collection_name=os.getenv("QDRANT_COLLECTION_TX", "finchat_tx_summaries"),
                    points_selector=[point_id]
                )
                logger.info(f"Deleted transaction {transaction_id} from Qdrant")
            except Exception as e:
                logger.warning(f"Failed to delete transaction {transaction_id} from Qdrant: {e}")
            
            Transaction.query.filter_by(plaid_transaction_id=transaction_id).delete()

        db.session.commit()
        print(f"DEBUG: Committed {len(added)} transactions to database")
    except Exception as e:
        print(f"DEBUG: Database commit failed with error: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        db.session.rollback()
        logger.error(f"Error updating transactions in the database: {e}")
        raise

async def update_accounts_in_db(plaid_item_id: str, accounts: list) -> None:
    """
    Update accounts in the database.

    Args:
        plaid_item_id: The Plaid item ID
        accounts: List of accounts fetched from the Plaid API
    """
    try:
        for account in accounts:
            existing_account = Account.query.filter_by(plaid_account_id=account['account_id']).first()
            if existing_account:
                # Update existing account
                existing_account.name = account.get('name')
                existing_account.mask = account.get('mask')
                existing_account.official_name = account.get('official_name')
                existing_account.current_balance = account.get('balances', {}).get('current')
                existing_account.available_balance = account.get('balances', {}).get('available')
                existing_account.iso_currency_code = account.get('balances', {}).get('iso_currency_code')
                existing_account.unofficial_currency_code = account.get('balances', {}).get('unofficial_currency_code')
                existing_account.type = str(account.get('type')) if account.get('type') else None  # Ensure type is a string
                existing_account.subtype = str(account.get('subtype')) if account.get('subtype') else None  # Ensure subtype is a string
            else:
                # Create new account
                new_account = Account(
                    plaid_account_id=account['account_id'],
                    item_id=Item.query.filter_by(plaid_item_id=plaid_item_id).first().id,
                    name=account.get('name'),
                    mask=account.get('mask'),
                    official_name=account.get('official_name'),
                    current_balance=account.get('balances', {}).get('current'),
                    available_balance=account.get('balances', {}).get('available'),
                    iso_currency_code=account.get('balances', {}).get('iso_currency_code'),
                    unofficial_currency_code=account.get('balances', {}).get('unofficial_currency_code'),
                    type=str(account.get('type')) if account.get('type') else None,  # Ensure type is a string
                    subtype=str(account.get('subtype')) if account.get('subtype') else None  # Ensure subtype is a string
                )
                db.session.add(new_account)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating accounts in the database: {e}")
        raise