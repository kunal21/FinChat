from db import db
from models import TimestampMixin


class Holding(db.Model, TimestampMixin):
    __tablename__ = "holdings_table"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts_table.id"), nullable=False)
    plaid_account_id = db.Column(db.Text, nullable=False)
    security_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    ticker_symbol = db.Column(db.Text)
    security_type = db.Column(db.Text)
    quantity = db.Column(db.Numeric(28, 10))
    institution_price = db.Column(db.Numeric(28, 10))
    institution_price_as_of = db.Column(db.DateTime(timezone=True))
    institution_value = db.Column(db.Numeric(28, 10))
    cost_basis = db.Column(db.Numeric(28, 10))
    iso_currency_code = db.Column(db.Text)
    unofficial_currency_code = db.Column(db.Text)
