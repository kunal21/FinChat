"""
Database queries for handling Plaid items and transactions.
"""

from typing import Dict, Any
from . import db
from models.item import Item
from models.transaction import Transaction


async def update_item_status(item_id: str, status: str) -> None:
    """
    Update the status of an item in the database.

    Args:
        item_id: The ID of the item to update
        status: The new status to set ('good' or 'bad')
    """
    item = Item.query.get(item_id)
    if item:
        item.status = status
        db.session.commit()

async def retrieve_item_by_plaid_item_id(plaid_item_id: str) -> Dict[str, Any]:
    """
    Retrieve an item from the database by its Plaid item ID.

    Args:
        plaid_item_id: The Plaid item ID to look up

    Returns:
        A dictionary containing the item's data
    """
    item = Item.query.filter_by(plaid_item_id=plaid_item_id).first()
    if not item:
        raise ValueError(f"No item found with Plaid item ID: {plaid_item_id}")
    return {
        'id': item.id,
        'plaid_item_id': item.plaid_item_id,
        'status': item.status,
        'access_token': item.plaid_access_token,
        'user_id': item.user_id
    } 