from flask import Blueprint, current_app, request, jsonify, abort
from models import User, Item, Account, Transaction     
from plaid_client import plaid_client
import logging
from db import db
from models import (AccountView, TransactionView, Message)
from utils import (
    sanitize_user,
    sanitize_item,
    sanitize_account,
    sanitize_transaction,
    sanitize_message
)

bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)


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

@bp.route("/users/<int:user_id>/messages", methods=["DELETE"])
def delete_user_messages(user_id):
    """Delete all messages for a user"""
    
    messages = Message.query.filter_by(user_id=user_id).all()
    for message in messages:
        db.session.delete(message)
        
    db.session.commit()
    
    # Emit a socket event to notify clients
    io = current_app.config['socketio']
    io.emit('DELETE_ALL_MESSAGES', {})

    return "", 204

@bp.route("/users/<int:user_id>/messages", methods=["GET"])
def get_user_messages(user_id):
    """Get all messages for a user"""
    
    messages = Message.query.filter_by(user_id=user_id).all()
    return jsonify([sanitize_message(msg) for msg in messages])