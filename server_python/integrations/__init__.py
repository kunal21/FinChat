"""
External API integrations and clients.

Singleton clients for third-party services:
- Plaid API for banking data
- OpenAI API for embeddings and LLM capabilities
"""

from .plaid_client import plaid_client, PlaidClient
from .openai_client import openai_client, OpenAIClient

__all__ = ["plaid_client", "PlaidClient", "openai_client", "OpenAIClient"]
