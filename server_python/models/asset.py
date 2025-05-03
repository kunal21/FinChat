from db import db
from models import TimestampMixin

class Asset(db.Model, TimestampMixin):
    __tablename__ = "assets_table"

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey("users_table.id"))
    value    = db.Column(db.Numeric(28, 2))
    description = db.Column(db.Text)

    user = db.relationship("User", back_populates="assets")
