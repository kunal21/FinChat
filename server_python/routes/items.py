from flask import Blueprint, current_app, request, jsonify, abort
from models import Item, Account, Transaction
from models import TransactionView  # Updated import
import logging
from db import db
from plaid_client import plaid_client
from update_transactions import update_transactions
import os   
from sqlalchemy import text
from utils import sanitize_item

bp = Blueprint("items", __name__)
logger = logging.getLogger(__name__)


# Create new item
@bp.route("/items", methods=["POST"])
async def create_item():
    data = request.get_json()
    public_token = data.get("publicToken")
    institution_id = data.get("institutionId")
    user_id = data.get("userId")

    if not all([public_token, institution_id, user_id]):
        abort(400, "Missing required fields")

    # Check for existing item
    existing_item = Item.query.filter_by(
        plaid_institution_id=institution_id,
        user_id=user_id
    ).first()
    
    if existing_item:
        abort(409, "You have already linked an item at this institution.")

    # Exchange public token for access token
    try:
        exchange_response = plaid_client.item_public_token_exchange(public_token)
        access_token = exchange_response['access_token']
        plaid_item_id = exchange_response['item_id']
        
        # Create new item
        new_item = Item(
            user_id=user_id,
            plaid_access_token=access_token,
            plaid_item_id=plaid_item_id,
            plaid_institution_id=institution_id,
            status='good'
        )
        db.session.add(new_item)
        db.session.commit()

        await update_transactions(plaid_item_id)
        io = current_app.config['socketio']
        io.emit('NEW_TRANSACTIONS_DATA', {'itemId': new_item.id})
        
        return jsonify(sanitize_item(new_item))
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        abort(500, str(e))

# Get single item
@bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(sanitize_item(item))

# Update item status
@bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item_status(item_id):
    data = request.get_json()
    status = data.get("status")
    
    if not status:
        abort(400, "You must provide updated item information.")
    
    valid_statuses = ['good', 'bad', 'login_required']  # Define your valid statuses
    if status not in valid_statuses:
        abort(400, f"Cannot set item status. Please use one of: {', '.join(valid_statuses)}")

    item = Item.query.get_or_404(item_id)
    item.status = status
    db.session.commit()
    
    return jsonify(sanitize_item(item))

# Delete item
@bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    try:
        # Remove item from Plaid
        plaid_client.remove_item(access_token=item.plaid_access_token)
        
        # Remove from database
        db.session.delete(item)
        db.session.commit()
        return "", 204
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        abort(500, "Item could not be removed in the Plaid API.")

# Get accounts for item
@bp.route("/items/<int:item_id>/accounts", methods=["GET"])
def get_item_accounts(item_id):
    accounts = Account.query.filter_by(item_id=item_id).all()
    return jsonify([{
        "id": acc.id,
        "item_id": acc.item_id,
        "name": acc.name,
        "mask": acc.mask,
        "official_name": acc.official_name,
        "current_balance": float(acc.current_balance) if acc.current_balance else None,
        "available_balance": float(acc.available_balance) if acc.available_balance else None,
        "iso_currency_code": acc.iso_currency_code,
        "unofficial_currency_code": acc.unofficial_currency_code,
        "type": acc.type,
        "subtype": acc.subtype,
        "created_at": acc.created_at.isoformat() if acc.created_at else None,
        "updated_at": acc.updated_at.isoformat() if acc.updated_at else None
    } for acc in accounts])

# Get transactions for item
@bp.route("/items/<int:item_id>/transactions", methods=["GET"])
def get_item_transactions(item_id):
    # Query the transactions view using ORM
    transactions = TransactionView.query.filter_by(item_id=item_id).all()

    return jsonify([{
        "id": tx.id,
        "account_id": tx.account_id,
        "item_id": tx.item_id,
        "user_id": tx.user_id,
        "name": tx.name,
        "type": tx.type,
        "date": tx.date.isoformat() if tx.date else None,
        "category": tx.category,
        "amount": float(tx.amount) if tx.amount else None,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
        "updated_at": tx.updated_at.isoformat() if tx.updated_at else None
    } for tx in transactions])

# Get items for user (moved from users route for consistency)
@bp.route("/users/<int:user_id>/items", methods=["GET"])
def items_by_user(user_id):
    items = Item.query.filter_by(user_id=user_id).all()
    return jsonify([sanitize_item(item) for item in items])

# Sandbox reset endpoint
@bp.route("/items/sandbox/item/reset_login", methods=["POST"])
def sandbox_reset():
    if os.getenv("PLAID_ENV") != "sandbox":
        abort(404)
    
    data = request.get_json()
    item_id = data.get("itemId")
    if not item_id:
        abort(400, "itemId required")
        
    item = Item.query.get_or_404(item_id)
    try:
        plaid_client.sandbox_item_reset_login(access_token=item.plaid_access_token)
        return jsonify({})
    except Exception as e:
        logger.error(f"Error resetting item: {str(e)}")
        abort(500, str(e))