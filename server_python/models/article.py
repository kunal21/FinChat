from sqlalchemy import Index
from sqlalchemy.orm import synonym
from sqlalchemy.dialects.postgresql import JSONB
from db import db


class Article(db.Model):
    __tablename__ = "articles"
    __table_args__ = (
        Index("idx_ticker", "ticker"),
        Index("idx_processed", "processed"),
        Index("idx_published_date", db.desc("published_at")),
    )

    id = db.Column(db.Text, primary_key=True)
    ticker = db.Column(db.String(10))
    title = db.Column(db.Text)
    headline = synonym("title")
    summary = db.Column(db.Text)
    url = db.Column(db.Text, unique=True, nullable=False)
    canonical_url = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.Text)
    published_at = db.Column(db.DateTime(timezone=True), nullable=False)
    raw_storage_key = db.Column(db.Text)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    is_material = db.Column(db.Boolean)
    structured_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    events = db.relationship("Event", back_populates="article")
    impacts = db.relationship("UserImpact", back_populates="article")
