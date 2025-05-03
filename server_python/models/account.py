from db import db
from models import TimestampMixin

class Account(db.Model, TimestampMixin):
    __tablename__ = "accounts_table"

    id          = db.Column(db.Integer, primary_key=True)
    item_id     = db.Column(db.Integer, db.ForeignKey("items_table.id"))
    plaid_account_id = db.Column(db.Text, unique=True, nullable=False)
    name        = db.Column(db.Text, nullable=False)
    mask        = db.Column(db.Text, nullable=False)
    official_name = db.Column(db.Text)
    current_balance       = db.Column(db.Numeric(28, 10))
    available_balance     = db.Column(db.Numeric(28, 10))
    iso_currency_code     = db.Column(db.Text)
    unofficial_currency_code = db.Column(db.Text)
    type        = db.Column(db.Text, nullable=False)
    subtype     = db.Column(db.Text, nullable=False)

    item        = db.relationship("Item", back_populates="accounts")
    transactions = db.relationship("Transaction", back_populates="account", cascade="all, delete")
