from flask import Blueprint, jsonify, abort
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from db import db
from models import Account, Holding
from integrations.plaid_client import plaid_client
import logging
from models import TransactionView
from models import AccountView
from core.utils import (
    sanitize_account,
    sanitize_transaction,
    sanitize_holding,
    parse_plaid_datetime,
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


# Get holdings for an investment account and store them
@bp.route("/accounts/<int:account_id>/holdings", methods=["GET"])
def get_account_holdings(account_id):
    account = Account.query.get_or_404(account_id)
    if account.type != "investment":
        return jsonify([])

    item = account.item
    if not item:
        abort(404, "Account has no linked item")

    try:
        request = InvestmentsHoldingsGetRequest(
            access_token=item.plaid_access_token,
            options={"account_ids": [account.plaid_account_id]},
        )
        response = plaid_client.client.investments_holdings_get(request)
    except Exception as exc:
        logger.exception("Error fetching holdings from Plaid: %s", exc)
        abort(502, "Failed to fetch holdings from Plaid")

    securities = {s["security_id"]: s for s in response.get("securities", [])}
    holdings = [
        h for h in response.get("holdings", [])
        if h.get("account_id") == account.plaid_account_id
    ]

    Holding.query.filter_by(account_id=account.id).delete()

    for holding in holdings:
        security = securities.get(holding.get("security_id"), {})
        row = Holding(
            account_id=account.id,
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

    stored = Holding.query.filter_by(account_id=account.id).all()
    return jsonify([sanitize_holding(h) for h in stored])
