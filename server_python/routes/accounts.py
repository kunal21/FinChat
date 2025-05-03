from flask import Blueprint, jsonify, abort
from models import Account, Transaction
import logging
from models import TransactionView
from models import AccountView

bp = Blueprint("accounts", __name__)
logger = logging.getLogger(__name__)

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
    """Sanitizes transaction data"""
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

# Get accounts for a user
@bp.route("/users/<int:user_id>/accounts", methods=["GET"])
def accounts_by_user(user_id):
    accounts = AccountView.query.filter_by(user_id=user_id).order_by(AccountView.id).all()
    return jsonify([sanitize_account(account) for account in accounts])

# Get transactions for an account
@bp.route("/accounts/<int:account_id>/transactions", methods=["GET"])
def get_account_transactions(account_id):
    transactions = TransactionView.query.filter_by(account_id=account_id)\
        .order_by(TransactionView.date.desc()).all()
    return jsonify([sanitize_transaction(tx) for tx in transactions])
