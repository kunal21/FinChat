import csv
from openai import OpenAI
import os

class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        openai_client_id = os.getenv('OPENAI_CLIENT_ID')
        self.client = OpenAI(
            api_key=openai_client_id,
        )

openai_client = OpenAIClient()
        