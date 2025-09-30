# backend/app/services/vectordb.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from typing import Optional, List, Dict, Any
from ..config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

client = QdrantClient(url=str(settings.QDRANT_URL), prefer_grpc=False, api_key=settings.QDRANT_API_KEY)


def ensure_collection(collection_name: str = None, vector_size: int = 1536):
    name = collection_name or settings.QDRANT_COLLECTION
    logger.info(f"Ensuring collection '{name}' exists with vector size {vector_size}")
    try:
        info = client.get_collection(name)
        logger.info(f"Collection '{name}' already exists: {info}")
        return info
    except Exception as e:
        logger.warning(f"Collection '{name}' not found, creating it. Error: {e}")
        try:
            client.recreate_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
            )
            info = client.get_collection(name)
            logger.info(f"Successfully created collection '{name}': {info}")
            return info
        except Exception as create_error:
            logger.error(f"Failed to create collection '{name}': {create_error}")
            raise


def upsert_spot(
    spot_id: str,
    embedding: List[float],
    metadata: Dict[str, Any],
    collection_name: str = None,
):
    name = collection_name or settings.QDRANT_COLLECTION
    logger.info(f"Upserting spot '{spot_id}' to collection '{name}' with metadata keys: {list(metadata.keys())}")
    try:
        point = qmodels.PointStruct(id=spot_id, vector=embedding, payload=metadata)
        result = client.upsert(collection_name=name, points=[point])
        logger.info(f"Successfully upserted spot '{spot_id}': {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to upsert spot '{spot_id}' to collection '{name}': {e}")
        raise


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
    logger.info(f"Searching vectors in collection '{name}' with top_k={top_k}, vector_dim={len(query_vector)}")
    
    try:
        resp = client.search(
            collection_name=name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        logger.info(f"Qdrant search returned {len(resp)} results")
        
        results = []
        for i, r in enumerate(resp):
            result = {"id": str(r.id), "score": float(r.score), "payload": r.payload}
            results.append(result)
            logger.debug(f"Result {i+1}: id={result['id']}, score={result['score']:.4f}, payload_keys={list(result['payload'].keys())}")
        
        logger.info(f"Processed {len(results)} search results")
        return results
        
    except Exception as e:
        logger.error(f"Failed to search vectors in collection '{name}': {e}")
        raise
