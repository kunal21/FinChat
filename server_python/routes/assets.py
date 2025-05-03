from flask import Blueprint, request, jsonify, abort
from models import Asset
import logging
from db import db

bp = Blueprint("assets", __name__)
logger = logging.getLogger(__name__)

def sanitize_asset(asset):
    """Sanitizes asset data"""
    return {
        "id": asset.id,
        "user_id": asset.user_id,
        "description": asset.description,
        "value": float(asset.value) if asset.value else None,
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
        "updated_at": asset.updated_at.isoformat() if asset.updated_at else None
    }

@bp.route("/assets", methods=["POST"])
def create_asset():
    """Create a new asset"""
    data = request.get_json()
    user_id = data.get("userId")
    description = data.get("description")
    value = data.get("value")

    if not all([user_id, description, value]):
        abort(400, "Missing required fields")

    asset = Asset(
        user_id=user_id,
        description=description,
        value=value
    )
    db.session.add(asset)
    db.session.commit()

    return jsonify(sanitize_asset(asset))

@bp.route("/assets/<int:user_id>", methods=["GET"])
def get_user_assets(user_id):
    """Get all assets for a user"""
    assets = Asset.query.filter_by(user_id=user_id).all()
    return jsonify([sanitize_asset(asset) for asset in assets])

@bp.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):
    """Delete an asset"""
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return "", 204
