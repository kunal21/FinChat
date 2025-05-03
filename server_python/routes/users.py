from flask import Blueprint, request, jsonify, abort
from models import User, Item, Account, Transaction     
from plaid_client import plaid_client
import logging
from db import db
from models import AccountView
from models import TransactionView

bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)

def sanitize_user(user):
    """Sanitizes user data"""
    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

def sanitize_item(item):
    """Sanitizes item data"""
    return {
        "id": item.id,
        "user_id": item.user_id,
        "plaid_institution_id": item.plaid_institution_id,
        "status": item.status,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None
    }

def sanitize_account(account):
    """Sanitizes account data"""
    return {
        "id": account.id,
        "item_id": account.item_id,
        "user_id": account.user_id,
        "name": account.name,
        "mask": account.mask,
        "official_name": account.official_name,
        "current_balance": float(account.current_balance) if account.current_balance else None,
        "available_balance": float(account.available_balance) if account.available_balance else None,
        "iso_currency_code": account.iso_currency_code,
        "unofficial_currency_code": account.unofficial_currency_code,
        "type": account.type,
        "subtype": account.subtype,
        "created_at": account.created_at.isoformat() if account.created_at else None,
        "updated_at": account.updated_at.isoformat() if account.updated_at else None
    }

def sanitize_transaction(transaction):
    """Sanitizes transaction"""
    return {
        "id": transaction.id,
        "account_id": transaction.account_id,
        "user_id": transaction.user_id,
        "name": transaction.name,
        "amount": float(transaction.amount) if transaction.amount else None,
        "date": transaction.date.isoformat() if transaction.date else None,
        "category": transaction.category,
        "type": transaction.type,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
        "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
    }

@bp.route("/users", methods=["GET"])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([sanitize_user(user) for user in users])

@bp.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    data = request.get_json()
    username = data.get("username")
    
    if not username:
        abort(400, "username required")
        
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        abort(409, "Username already exists")
        
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    
    return jsonify([sanitize_user(user)])

@bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get a single user"""
    user = User.query.get_or_404(user_id)
    return jsonify([sanitize_user(user)])

@bp.route("/users/<int:user_id>/items", methods=["GET"])
def get_user_items(user_id):
    """Get all items for a user"""
    items = Item.query.filter_by(user_id=user_id).all()
    return jsonify([sanitize_item(item) for item in items])

@bp.route("/users/<int:user_id>/accounts", methods=["GET"])
def get_user_accounts(user_id):
    """Get all accounts for a user"""
    accounts = AccountView.query.filter(AccountView.user_id == user_id).all()
    return jsonify([sanitize_account(account) for account in accounts])

@bp.route("/users/<int:user_id>/transactions", methods=["GET"])
def get_user_transactions(user_id):
    """Get all transactions for a user"""
    transactions = TransactionView.query.filter(TransactionView.user_id == user_id).all()
    return jsonify([sanitize_transaction(tx) for tx in transactions])

@bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user and all associated items"""
    user = User.query.get_or_404(user_id)
    
    # Remove items from Plaid first
    items = Item.query.filter_by(user_id=user_id).all()
    for item in items:
        try:
            plaid_client.remove_item(item.plaid_access_token)
        except Exception as e:
            logger.error(f"Error removing Plaid item: {str(e)}")
            
    # Delete user from database (will cascade to items, accounts, and transactions)
    db.session.delete(user)
    db.session.commit()
    
    return "", 204
