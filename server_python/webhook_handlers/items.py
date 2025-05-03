"""
Defines the handler for Item webhooks.
https://plaid.com/docs/#item-webhooks
"""

from typing import Dict, Any
from db.queries import update_item_status, retrieve_item_by_plaid_item_id

async def item_error_handler(plaid_item_id: str, error: Dict[str, Any]) -> None:
    """
    Handles Item errors received from item webhooks. When an error is received
    different operations are needed to update an item based on the error_code
    that is encountered.

    Args:
        plaid_item_id: The Plaid ID of an item
        error: The error received from the webhook
    """
    error_code = error.get('error_code')
    if error_code == 'ITEM_LOGIN_REQUIRED':
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        await update_item_status(item['id'], 'bad')
    else:
        print(f'WEBHOOK: ITEMS: Plaid item id {plaid_item_id}: unhandled ITEM error')

async def items_handler(request_body: Dict[str, Any], io: Any) -> None:
    """
    Handles all Item webhook events.

    Args:
        request_body: The request body of an incoming webhook event
        io: A socket.io server instance
    """
    webhook_code = request_body.get('webhook_code')
    plaid_item_id = request_body.get('item_id')
    error = request_body.get('error')

    def server_log_and_emit_socket(additional_info: str, item_id: str, error_code: str = None) -> None:
        print(f'WEBHOOK: ITEMS: {webhook_code}: Plaid item id {plaid_item_id}: {additional_info}')
        if webhook_code:
            io.emit(webhook_code, {'itemId': item_id, 'errorCode': error_code})

    if webhook_code == 'WEBHOOK_UPDATE_ACKNOWLEDGED':
        server_log_and_emit_socket('is updated', plaid_item_id, error)
    elif webhook_code == 'ERROR':
        await item_error_handler(plaid_item_id, error)
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        server_log_and_emit_socket(
            f'ERROR: {error["error_code"]}: {error["error_message"]}',
            item['id'],
            error['error_code']
        )
    elif webhook_code in ['PENDING_EXPIRATION', 'PENDING_DISCONNECT']:
        item = await retrieve_item_by_plaid_item_id(plaid_item_id)
        await update_item_status(item['id'], 'bad')
        server_log_and_emit_socket(
            'user needs to re-enter login credentials',
            item['id'],
            error
        )
    else:
        server_log_and_emit_socket(
            'unhandled webhook type received.',
            plaid_item_id,
            error
        )
