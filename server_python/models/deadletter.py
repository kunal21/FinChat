from db import db
from sqlalchemy.dialects.postgresql import JSONB


class Deadletter(db.Model):
    __tablename__ = "deadletter"

    id = db.Column(db.Text, primary_key=True)
    stage = db.Column(db.Text)
    url = db.Column(db.Text)
    error = db.Column(db.Text)
    payload_json = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
