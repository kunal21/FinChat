# server_python/routes/link_events.py
from flask import Blueprint, request, jsonify
from models import LinkEvent
import logging
from db import db       

bp = Blueprint("link_events", __name__)
logger = logging.getLogger(__name__)

@bp.route("/link-event", methods=["POST"])
def create_link_event():
    data = request.get_json()
    event = LinkEvent(
        user_id=data.get('userId'),
        type=data.get('type'),
        link_session_id=data.get('link_session_id'),
        request_id=data.get('request_id'),
        error_type=data.get('error_type'),
        error_code=data.get('error_code')
    )
    db.session.add(event)
    db.session.commit()
    return "", 200