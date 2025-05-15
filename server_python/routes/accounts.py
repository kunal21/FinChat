from flask import Blueprint, jsonify, abort
from models import Account, Transaction
import logging
from models import TransactionView
from models import AccountView
from utils import (
    sanitize_account,
    sanitize_transaction
)

bp = Blueprint("accounts", __name__)
logger = logging.getLogger(__name__)


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
