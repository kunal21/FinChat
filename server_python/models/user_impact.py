from sqlalchemy import Index
from db import db

class UserImpact(db.Model):
    __tablename__ = "user_impacts"
    __table_args__ = (
        Index("idx_user_unread", "user_id", "read", "dismissed"),
        Index("idx_created_date", db.desc("created_at")),
    )

    id = db.Column(db.Text, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users_table.id"), nullable=False)
    article_id = db.Column(db.Text, db.ForeignKey("articles.id"), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    
    impact_level = db.Column(db.String(10), nullable=False)  # HIGH/MEDIUM/LOW
    impact_summary = db.Column(db.Text, nullable=False)
    estimated_effect = db.Column(db.String(100))
    
    read = db.Column(db.Boolean, default=False, nullable=False)
    dismissed = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    article = db.relationship("Article", back_populates="impacts")
    user = db.relationship("User", back_populates="impacts")
