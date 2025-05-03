from db import db
from models import TimestampMixin

class Item(db.Model, TimestampMixin):
    __tablename__ = "items_table"

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("users_table.id"))
    plaid_access_token  = db.Column(db.Text, unique=True, nullable=False)
    plaid_item_id       = db.Column(db.Text, unique=True, nullable=False)
    plaid_institution_id = db.Column(db.Text, nullable=False)
    status              = db.Column(db.Text, nullable=False)
    transactions_cursor = db.Column(db.Text)

    # relationships
    user      = db.relationship("User",     back_populates="items")
    accounts  = db.relationship("Account",  back_populates="item", cascade="all, delete")
