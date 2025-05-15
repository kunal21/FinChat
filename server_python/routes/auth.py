from flask import Blueprint, request, jsonify, abort
from models import User
import logging
from utils import sanitize_user

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

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
