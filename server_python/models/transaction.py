from db import db
from models import TimestampMixin

class Transaction(db.Model, TimestampMixin):
    __tablename__ = "transactions_table"

    id          = db.Column(db.Integer, primary_key=True)
    account_id  = db.Column(db.Integer, db.ForeignKey("accounts_table.id"))
    plaid_transaction_id = db.Column(db.Text, unique=True, nullable=False)
    plaid_category_id    = db.Column(db.Text)
    category    = db.Column(db.Text)
    personal_finance_category_primary = db.Column(db.Text)
    personal_finance_category_detailed = db.Column(db.Text)
    type        = db.Column(db.Text, nullable=False)
    name        = db.Column(db.Text, nullable=False)
    amount      = db.Column(db.Numeric(28, 10), nullable=False)
    iso_currency_code     = db.Column(db.Text)
    unofficial_currency_code = db.Column(db.Text)
    date        = db.Column(db.Date, nullable=False)
    pending     = db.Column(db.Boolean, nullable=False)
    account_owner = db.Column(db.Text)

    account = db.relationship("Account", back_populates="transactions")
