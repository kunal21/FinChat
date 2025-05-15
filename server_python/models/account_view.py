from db import db
from sqlalchemy import Table
class AccountView(db.Model):
    __tablename__ = 'accounts'  # Map to the accounts view
    __table_args__ = {'extend_existing': True}  # Allow reuse if already defined

    id = db.Column(db.Integer, primary_key=True)
    plaid_account_id = db.Column(db.String)
    item_id = db.Column(db.Integer)
    plaid_item_id = db.Column(db.String)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String)
    mask = db.Column(db.String)
    official_name = db.Column(db.String)
    current_balance = db.Column(db.Float)
    available_balance = db.Column(db.Float)
    iso_currency_code = db.Column(db.String)
    unofficial_currency_code = db.Column(db.String)
    type = db.Column(db.String)
    subtype = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
