from plaid_client import plaid_client
from flask import Blueprint, request, jsonify
import logging

bp = Blueprint("institutions", __name__)
logger = logging.getLogger(__name__)

def to_array(item):
    """Convert single item or list to array format"""
    if not isinstance(item, list):
        return [item] if item else []
    return item

@bp.route("/institutions", methods=["GET"])
def get_institutions():
    """Get institutions from Plaid API"""
    try:
        count = int(request.args.get('count', 200))
        offset = int(request.args.get('offset', 0))
        
        request_data = {
            "count": count,
            "offset": offset,
            "options": {
                "include_optional_metadata": True
            }
        }
        
        response = plaid_client.get_institutions(request_data)
        institutions = response.get('institutions', [])
        return jsonify(to_array(institutions))
    except Exception as e:
        logger.error(f"Error getting institutions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/institutions/<institution_id>", methods=["GET"])
def get_institution(institution_id):
    """Get a single institution from Plaid API"""
    try:
        request_data = {
            "institution_id": institution_id,
            "country_codes": ["US"],
            "options": {
                "include_optional_metadata": True
            }
        }
        institution = plaid_client.get_institution_by_id(request_data)  
        return jsonify(institution.to_dict())
    except Exception as e:
        logger.error(f"Error getting institution: {str(e)}")
        return jsonify({"error": str(e)}), 500
