from db import db
from sqlalchemy.dialects.postgresql import JSONB


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Text, primary_key=True)
    article_id = db.Column(db.Text, db.ForeignKey("articles.id"))
    domain = db.Column(db.Text)
    topic = db.Column(db.Text)
    event_type = db.Column(db.Text)
    summary = db.Column(db.Text)
    entities_json = db.Column(JSONB)
    confidence = db.Column(db.Float)
    model = db.Column(db.Text)
    prompt_version = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    article = db.relationship("Article", back_populates="events")
