# server_python/routes/link_tokens.py
from flask import Blueprint, request, jsonify
from plaid_client import plaid_client
import requests
import os
from models import Item
import logging  
from db import db 

bp = Blueprint("link_tokens", __name__)
logger = logging.getLogger(__name__)

@bp.route("/link-token", methods=["POST"])
def create_link_token():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        item_id = data.get('itemId')

        access_token = None
        products = ['transactions']  # must include transactions for webhooks

        if item_id is not None:
            item = Item.query.get_or_404(item_id)
            access_token = item.plaid_access_token
            products = []

        # Get ngrok URL for webhook
        response = requests.get('http://ngrok:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        https_tunnel = next(t for t in tunnels if t['proto'] == 'https')

        link_token_params = {
            'user': {
                'client_user_id': f'user_{user_id}'
            },
            'client_name': 'FinChat',
            'products': products,
            'country_codes': ['US'],
            'language': 'en',
            'webhook': f"{https_tunnel['public_url']}/services/webhook",
        }

        if access_token:
            link_token_params['access_token'] = access_token

        # Add redirect URI if configured
        redirect_uri = os.getenv('PLAID_REDIRECT_URI')
        if redirect_uri and redirect_uri.startswith('http'):
            link_token_params['redirect_uri'] = redirect_uri

        response = plaid_client.create_link_token(link_token_params)
        return jsonify(response.to_dict())
    except Exception as e:
        logger.error(f"Error creating link token: {str(e)}")
        return jsonify({"error": str(e)}), 500