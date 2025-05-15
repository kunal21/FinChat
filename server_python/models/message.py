from db import db
from models import TimestampMixin

class Message(db.Model, TimestampMixin):
    __tablename__ = "messages_table"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users_table.id"), nullable=False)
    text        = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, nullable=False)
    
    user        = db.relationship("User", back_populates="messages")