from flask import Blueprint, current_app, request, jsonify, abort
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from models import User, Item, Account, Transaction, Holding, UserImpact
from integrations.plaid_client import plaid_client
import logging
from db import db
from models import (AccountView, TransactionView, Message)
from core.utils import (
    sanitize_user,
    sanitize_item,
    sanitize_account,
    sanitize_transaction,
    sanitize_message,
    sanitize_holding,
    sanitize_user_impact,
    parse_plaid_datetime,
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

@bp.route("/users/<int:user_id>/holdings", methods=["GET"])
def get_user_holdings(user_id):
    """Fetch and store investment holdings for a user"""
    accounts = (
        Account.query.join(Item, Account.item_id == Item.id)
        .filter(Item.user_id == user_id)
        .all()
    )
    investment_accounts = [acct for acct in accounts if acct.type == "investment"]
    if not investment_accounts:
        return jsonify([])

    accounts_by_item = {}
    for acct in investment_accounts:
        accounts_by_item.setdefault(acct.item_id, []).append(acct)

    for item_id, item_accounts in accounts_by_item.items():
        item = item_accounts[0].item
        if not item:
            continue
        plaid_account_ids = [acct.plaid_account_id for acct in item_accounts]
        account_id_map = {acct.plaid_account_id: acct.id for acct in item_accounts}

        try:
            request = InvestmentsHoldingsGetRequest(
                access_token=item.plaid_access_token,
                options={"account_ids": plaid_account_ids},
            )
            response = plaid_client.client.investments_holdings_get(request)
        except Exception as exc:
            logger.exception("Error fetching holdings from Plaid: %s", exc)
            abort(502, "Failed to fetch holdings from Plaid")

        securities = {s["security_id"]: s for s in response.get("securities", [])}
        holdings = [
            h for h in response.get("holdings", [])
            if h.get("account_id") in account_id_map
        ]

        Holding.query.filter(Holding.account_id.in_(account_id_map.values())).delete(
            synchronize_session=False
        )

        for holding in holdings:
            security = securities.get(holding.get("security_id"), {})
            row = Holding(
                account_id=account_id_map.get(holding.get("account_id")),
                plaid_account_id=holding.get("account_id", ""),
                security_id=holding.get("security_id", ""),
                name=security.get("name"),
                ticker_symbol=security.get("ticker_symbol"),
                security_type=security.get("type"),
                quantity=holding.get("quantity"),
                institution_price=holding.get("institution_price"),
                institution_price_as_of=parse_plaid_datetime(
                    holding.get("institution_price_as_of")
                ),
                institution_value=holding.get("institution_value"),
                cost_basis=holding.get("cost_basis"),
                iso_currency_code=holding.get("iso_currency_code")
                or security.get("iso_currency_code"),
                unofficial_currency_code=holding.get("unofficial_currency_code")
                or security.get("unofficial_currency_code"),
            )
            db.session.add(row)

    db.session.commit()

    account_ids = [acct.id for acct in investment_accounts]
    stored = Holding.query.filter(Holding.account_id.in_(account_ids)).all()
    return jsonify([sanitize_holding(h) for h in stored])

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

@bp.route("/users/<int:user_id>/impacts", methods=["GET"])
def get_user_impacts(user_id):
    """Get portfolio impact notifications for a user"""

    # Verify user exists
    user = User.query.get_or_404(user_id)

    # Get query parameters for filtering
    unread_only = request.args.get("unread_only", "false").lower() == "true"

    # Build query
    query = UserImpact.query.filter_by(user_id=user_id)

    # Filter by read/dismissed status if requested
    if unread_only:
        query = query.filter_by(read=False, dismissed=False)

    # Order by creation date (newest first)
    impacts = query.order_by(UserImpact.created_at.desc()).all()

    return jsonify([sanitize_user_impact(impact) for impact in impacts])

@bp.route("/users/<int:user_id>/impacts/<impact_id>", methods=["PATCH"])
def update_user_impact(user_id, impact_id):
    """Update a user impact (mark as read or dismissed)"""

    impact = UserImpact.query.filter_by(id=impact_id, user_id=user_id).first_or_404()

    data = request.get_json()

    if "read" in data:
        impact.read = bool(data["read"])

    if "dismissed" in data:
        impact.dismissed = bool(data["dismissed"])

    db.session.commit()

    return jsonify(sanitize_user_impact(impact))
