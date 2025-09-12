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

    def embed_texts(self, texts):
        """Return embeddings for a list of texts using the embeddings API."""
        import os
        if not isinstance(texts, list):
            texts = [texts]
        model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        resp = self.client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]
    
    

openai_client = OpenAIClient()
        