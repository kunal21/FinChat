from flask import Blueprint, request, jsonify, abort
from models import User
import logging

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

def sanitize_user(user):
    """ Sanitizes user data """
    if user is None: 
        return None
    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

@bp.route("/sessions", methods=["POST"])
def login_user():
    data = request.get_json(force=True)
    
    username = data.get("username")
    if not username:
        abort(400, "username missing")

    user = User.query.filter_by(username=username).first()
    if user is not None:
        # User exists, return sanitized user data in an array
        return jsonify([sanitize_user(user)])
    else:
        # User doesn't exist, return null
        return jsonify(None)
