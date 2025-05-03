"""
Defines the handler for unhandled webhook types.
"""

from typing import Dict, Any

async def unhandled_webhook(request_body: Dict[str, Any], io: Any) -> None:
    """
    Handles any webhook events that don't have a specific handler.

    Args:
        request_body: The request body of an incoming webhook event
        io: A socket.io server instance
    """
    webhook_type = request_body.get('webhook_type')
    webhook_code = request_body.get('webhook_code')
    item_id = request_body.get('item_id')

    print(
        f'WEBHOOK: {webhook_type}: {webhook_code}: Plaid item id {item_id}: '
        'unhandled webhook type received.'
    )
