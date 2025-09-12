"""
Defines the handler for Transactions webhooks.
https://plaid.com/docs/#transactions-webhooks
"""

from typing import Dict, Any
from db.queries import retrieve_item_by_plaid_item_id
from update_transactions import update_transactions

async def handle_transactions_webhook(request_body: Dict[str, Any], io: Any) -> None:
    """
    Handles all transaction webhook events. The transaction webhook notifies
    you that a single item has new transactions available.

    Args:
        request_body: The request body of an incoming webhook event
        io: A socket.io server instance
    """
    webhook_code = request_body.get('webhook_code')
    plaid_item_id = request_body.get('item_id')
    
    print(f"DEBUG: Received webhook: {webhook_code} for item {plaid_item_id}")
    print(f"DEBUG: Socket.io instance: {io}")

    def server_log_and_emit_socket(additional_info: str, item_id: str) -> None:
        print(
            f'WEBHOOK: TRANSACTIONS: {webhook_code}: Plaid_item_id {plaid_item_id}: {additional_info}'
        )
        if webhook_code:
            if webhook_code in ['HISTORICAL_UPDATE', 'INITIAL_UPDATE', 'DEFAULT_UPDATE']:
                io.emit('HISTORICAL_UPDATE', {'itemId': item_id})
            else:
                io.emit(webhook_code, {'itemId': item_id})

    if webhook_code == 'SYNC_UPDATES_AVAILABLE':
        # Fired when new transactions data becomes available
        result = await update_transactions(plaid_item_id)
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        server_log_and_emit_socket(
            f'Transactions: {result["added_count"]} added, '
            f'{result["modified_count"]} modified, '
            f'{result["removed_count"]} removed',
            item['id']
        )
        # Emit a canonical event so clients always refresh transactions for this item
        try:
            io.emit('NEW_TRANSACTIONS_DATA', {'itemId': item['id']})
            print(f"DEBUG: Emitted NEW_TRANSACTIONS_DATA for item {item['id']}")
        except Exception as e:
            print(f"DEBUG: Failed to emit NEW_TRANSACTIONS_DATA: {e}")
    elif webhook_code in ['DEFAULT_UPDATE', 'INITIAL_UPDATE', 'HISTORICAL_UPDATE']:
        result = await update_transactions(plaid_item_id)
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        server_log_and_emit_socket(
            f'Historical transactions: {result["added_count"]} added, '
            f'{result["modified_count"]} modified, '
            f'{result["removed_count"]} removed',
            item['id']
        )
        try:
            io.emit('NEW_TRANSACTIONS_DATA', {'itemId': item['id']})
            print(f"DEBUG: Emitted NEW_TRANSACTIONS_DATA for item {item['id']}")
        except Exception as e:
            print(f"DEBUG: Failed to emit NEW_TRANSACTIONS_DATA: {e}")
    else:
        server_log_and_emit_socket('unhandled webhook type received.', plaid_item_id)
