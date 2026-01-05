"""
Defines the handler for Transactions webhooks.
https://plaid.com/docs/#transactions-webhooks
"""

from typing import Dict, Any
from db.queries import retrieve_item_by_plaid_item_id
from jobs import update_transactions

async def handle_transactions_webhook(request_body: Dict[str, Any], io: Any) -> None:
    """
    Handles all transaction webhook events. The transaction webhook notifies
    you that a single item has new transactions available.

    Args:
        request_body: The request body of an incoming webhook event
        io: A socket.io server instance
    """
    webhook_type = request_body.get('webhook_type')
    webhook_code = request_body.get('webhook_code')
    plaid_item_id = request_body.get('item_id')

    update_like = {'SYNC_UPDATES_AVAILABLE', 'INITIAL_UPDATE', 'HISTORICAL_UPDATE'}
    if webhook_type == 'TRANSACTIONS' and webhook_code in update_like:
        try:
            # 1) run sync (writes rows + commits)
            result = await update_transactions(plaid_item_id)

            # 2) map plaid_item_id -> numeric DB item id
            item = await retrieve_item_by_plaid_item_id(plaid_item_id)
            numeric_item_id = item['id'] if isinstance(item, dict) else item.id

            # 3) notify UI to refetch
            try:
                io.emit('NEW_TRANSACTIONS_DATA', {'itemId': numeric_item_id})
            except Exception as e:
                print(f"ERROR: Failed to emit socket event: {e}")
                
            return
            
        except Exception as e:
            print(f"ERROR: Transaction webhook processing failed for item {plaid_item_id}: {e}")
            print(f"ERROR: Exception type: {type(e)}")
            # Still try to emit an error event to the UI
            try:
                item = await retrieve_item_by_plaid_item_id(plaid_item_id)
                numeric_item_id = item['id'] if isinstance(item, dict) else item.id
                io.emit('TRANSACTION_SYNC_ERROR', {'itemId': numeric_item_id, 'error': str(e)})
            except:
                pass
            raise
    else:
        print(f"DEBUG: Unhandled webhook type/code: {webhook_type}/{webhook_code}")
    
    