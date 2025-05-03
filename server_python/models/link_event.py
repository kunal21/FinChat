from db import db
from models import TimestampMixin

class LinkEvent(db.Model):
    __tablename__ = "link_events_table"

    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.Text, nullable=False)
    user_id        = db.Column(db.Integer)
    link_session_id = db.Column(db.Text)
    request_id     = db.Column(db.Text, unique=True)
    error_type     = db.Column(db.Text)
    error_code     = db.Column(db.Text)
    status         = db.Column(db.Text)
    created_at     = db.Column(db.DateTime(timezone=True), server_default=db.func.now())