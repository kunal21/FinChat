import os
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

# Collections from env (names are configurable)
COLL_MESSAGES = os.getenv("QDRANT_COLLECTION_MESSAGES", "finchat_messages")
COLL_TX       = os.getenv("QDRANT_COLLECTION_TX", "finchat_tx_summaries")
COLL_FILES    = os.getenv("QDRANT_COLLECTION_FILES", "finchat_files")  # optional

VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "1536"))  # text-embedding-3-small
DISTANCE    = Distance.COSINE

class VectorStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        api_key = os.getenv("QDRANT_API_KEY") or None

        self.client = QdrantClient(host=host, port=port, api_key=api_key)
        self._ensure_collection(COLL_MESSAGES)
        self._ensure_collection(COLL_TX)
        # Optional receipts/files
        if COLL_FILES:
            self._ensure_collection(COLL_FILES)

    def _ensure_collection(self, collection_name: str) -> None:
        collections = self.client.get_collections().collections
        names = {c.name for c in collections}
        if collection_name not in names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
            )

    # ---------- Generic helpers ----------
    def upsert_point(self, collection: str, point_id: int | str, vector: List[float], payload: Dict[str, Any]) -> None:
        self.client.upsert(collection_name=collection, points=[PointStruct(id=point_id, vector=vector, payload=payload)])

    def search(self, collection: str, vector: List[float], user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        flt = Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))])
        res = self.client.search(collection_name=collection, query_vector=vector, limit=limit, query_filter=flt)
        return [r.payload for r in res]

    # ---------- Domain-specific convenience ----------
    def upsert_message(self, point_id: int | str, user_id: str, vector: List[float], text: str, author: str, extra: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {"user_id": user_id, "text": text, "author": author}
        if extra:
            payload.update(extra)
        self.upsert_point(COLL_MESSAGES, point_id, vector, payload)

    def upsert_tx_summary(self, point_id: int | str, user_id: str, vector: List[float], text: str, summary_type: str, extra: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {"user_id": user_id, "text": text, "type": summary_type}
        if extra:
            payload.update(extra)
        self.upsert_point(COLL_TX, point_id, vector, payload)

    def upsert_file_note(self, point_id: int | str, user_id: str, vector: List[float], text: str, extra: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {"user_id": user_id, "text": text}
        if extra:
            payload.update(extra)
        if COLL_FILES:
            self.upsert_point(COLL_FILES, point_id, vector, payload)

    def search_messages(self, user_id: str, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        return self.search(COLL_MESSAGES, vector, user_id, limit)

    def search_tx(self, user_id: str, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        return self.search(COLL_TX, vector, user_id, limit)

    def search_files(self, user_id: str, vector: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        if not COLL_FILES:
            return []
        return self.search(COLL_FILES, vector, user_id, limit)