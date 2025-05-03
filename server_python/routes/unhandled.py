# server_python/routes/unhandled.py
from flask import Blueprint, abort

bp = Blueprint("unhandled", __name__)

@bp.route("/*", methods=["GET", "POST", "PUT", "DELETE"])
def handle_unhandled():
    abort(404, description="not found")