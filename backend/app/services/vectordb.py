# backend/app/services/vectordb.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from typing import Optional, List, Dict, Any
from ..config import settings
import uuid

client = QdrantClient(url=str(settings.QDRANT_URL), prefer_grpc=False, api_key=settings.QDRANT_API_KEY)


def ensure_collection(collection_name: str = None, vector_size: int = 1536):
    name = collection_name or settings.QDRANT_COLLECTION
    try:
        info = client.get_collection(name)
        return info
    except Exception:
        client.recreate_collection(
            collection_name=name,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )
        return client.get_collection(name)


def upsert_spot(
    spot_id: str,
    embedding: List[float],
    metadata: Dict[str, Any],
    collection_name: str = None,
):
    name = collection_name or settings.QDRANT_COLLECTION
    point = qmodels.PointStruct(id=spot_id, vector=embedding, payload=metadata)
    client.upsert(collection_name=name, points=[point])


def search_vectors(
    query_vector: List[float],
    top_k: int = 10,
    collection_name: str = None,
    filter_payload: Optional[Dict] = None,
) -> List[Dict]:
    """
    Returns list of results with fields: id, score, payload (metadata)
    """
    name = collection_name or settings.QDRANT_COLLECTION
    resp = client.search(
        collection_name=name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        with_vector=False,
    )
    results = []
    for r in resp:
        results.append({"id": str(r.id), "score": float(r.score), "payload": r.payload})
    return results
