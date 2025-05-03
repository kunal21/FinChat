from db import db
from models import TimestampMixin

class PlaidApiEvent(db.Model):
    __tablename__ = "plaid_api_events_table"

    id          = db.Column(db.Integer, primary_key=True)
    item_id     = db.Column(db.Integer)
    user_id     = db.Column(db.String)
    plaid_method = db.Column(db.Text, nullable=False)
    arguments   = db.Column(db.Text)
    request_id  = db.Column(db.Text, unique=True)
    error_type  = db.Column(db.Text)
    error_code  = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
