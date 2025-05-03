# server_python/plaid.py
import json
import plaid
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api_client import ApiClient
import os
import logging
from flask import jsonify
from db import db
from models.plaid_api_event import PlaidApiEvent
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class PlaidClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaidClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        plaid_client_id = os.getenv('PLAID_CLIENT_ID')
        plaid_secret = os.getenv('PLAID_SECRET_SANDBOX')

        configuration = Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': plaid_client_id,
                'secret': plaid_secret,
                'plaidVersion': '2020-09-14'
            }
        )

        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        self._initialized = True

    def log_plaid_api_event(self, item_id, user_id, plaid_method, args, response):
        """Log Plaid API events to database"""
        try:
            event = PlaidApiEvent(
                item_id=item_id,
                user_id=user_id,
                plaid_method=plaid_method,
                arguments=str(args),
                request_id=getattr(response, 'request_id', None),
                error_type=getattr(response, 'error_type', None),
                error_code=getattr(response, 'error_code', None)
            )
            db.session.add(event)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error logging Plaid API event: {str(e)}")

    def item_public_token_exchange(self, public_token):
        """Exchange public token for access token"""
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            response = self.client.item_public_token_exchange(request)
            self.log_plaid_api_event(
                None, None, 'itemPublicTokenExchange',
                {'public_token': public_token}, response
            )
            return response
        except Exception as e:
            self.log_plaid_api_event(
                None, None, 'itemPublicTokenExchange',
                {'public_token': public_token}, e
            )
            raise

    def create_link_token(self, link_token_params):
        """Create a Link token for initialization"""
        try:
            user_id = link_token_params['user']['client_user_id']

            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id='user_3',
                    phone_number='+1 415 5550123'
                ),
                client_name=link_token_params['client_name'],
                products=[Products('transactions')],
                country_codes=[CountryCode('US')],
                language='en',
                webhook=link_token_params['webhook'],
                access_token=link_token_params.get('access_token', None)
            )

            response = self.client.link_token_create(request)
            self.log_plaid_api_event(
                None, user_id, 'linkTokenCreate',
                request.to_dict(), response
            )
            return response
        except plaid.ApiException as e:
            return json.loads(e.body)
   
    def get_accounts(self, access_token, item_id=None, user_id=None):
        """Get accounts for an Item"""
        try:
            response = self.client.accounts_get({
                'access_token': access_token
            })
            self.log_plaid_api_event(
                item_id, user_id, 'accountsGet',
                {'access_token': access_token}, response
            )
            
            return response
        except Exception as e:
            self.log_plaid_api_event(
                item_id, user_id, 'accountsGet',
                {'access_token': access_token}, e
            )
            raise

    def get_item(self, access_token):
        """Get item information"""
        try:
            response = self.client.item_get({
                'access_token': access_token
            })
            return response
        except Exception as e:
            raise

    def remove_item(self, access_token):
        """Remove an item"""
        try:
            response = self.client.item_remove({
                'access_token': access_token
            })
            return response
        except Exception as e:
            raise

    def sandbox_item_reset_login(self, access_token):
        """Reset a sandbox item's login state"""
        try:
            response = self.client.sandbox_item_reset_login({
                'access_token': access_token
            })  
            return response
        except Exception as e:
            raise    

    def get_institution_by_id(self, request_data):
        """Get an institution by ID"""
        try:
            # request_data = {
            # "institution_id": institution_id,
            # "country_codes": ["US"],
            # "options": {
            #         "include_optional_metadata": True
            #     }
            # }
            request_data['country_codes'][0] = CountryCode('US')
            request = InstitutionsGetByIdRequest(
                institution_id=request_data['institution_id'],
                country_codes=request_data['country_codes'],
            )
            response = self.client.institutions_get_by_id(request)
            return response
        except Exception as e:
            raise       
    
    def get_institutions(self, request_data):
        """Get institutions"""
        try:
            response = self.client.institutions_get(request_data)
            return response
        except Exception as e:
            raise       

# Create a singleton instance
plaid_client = PlaidClient()