from db import db
from sqlalchemy import Table
class TransactionView(db.Model):
    __tablename__ = 'transactions'  # Map to the transactions view
    __table_args__ = {'extend_existing': True}  # Allow reuse if already defined

    id = db.Column(db.Integer, primary_key=True)
    plaid_transaction_id = db.Column(db.String)
    account_id = db.Column(db.Integer)
    plaid_account_id = db.Column(db.String)
    item_id = db.Column(db.Integer)
    plaid_item_id = db.Column(db.String)
    user_id = db.Column(db.Integer)
    category = db.Column(db.String)
    personal_finance_category_primary = db.Column(db.String)
    personal_finance_category_detailed = db.Column(db.String)
    type = db.Column(db.String)
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    iso_currency_code = db.Column(db.String)
    unofficial_currency_code = db.Column(db.String)
    date = db.Column(db.Date)
    pending = db.Column(db.Boolean)
    account_owner = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
