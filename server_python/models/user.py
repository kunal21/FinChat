from db import db
from models import TimestampMixin

class User(db.Model, TimestampMixin):
    __tablename__ = "users_table"

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)

    # relationships
    items   = db.relationship("Item",   back_populates="user", cascade="all, delete")
    assets  = db.relationship("Asset",  back_populates="user", cascade="all, delete")
