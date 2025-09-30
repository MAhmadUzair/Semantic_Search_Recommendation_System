from fastapi import APIRouter, HTTPException
from ..models.spots import SpotCreate, SpotResponse
from ..services.embeddings import embed_text
from ..services.vectordb import upsert_spot, ensure_collection
import uuid
from ..config import settings
from typing import Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/spots", tags=["spots"])



@router.post("/", response_model=SpotResponse)
def create_spot(payload: SpotCreate):
    # Ensure collection exists before creating spot
    try:
        ensure_collection(collection_name=settings.QDRANT_COLLECTION, vector_size=1536)
    except Exception as e:
        logger.error(f"Failed to ensure collection: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    
    spot_id = str(uuid.uuid4())
    full_text = f"{payload.title} {payload.description or ''} {' '.join(payload.category_tags or [])}"
    embedding = embed_text([full_text], model=settings.EMBEDDING_MODEL)[0]
    metadata: Dict = {
        "title": payload.title,
        "description": payload.description,
        "category_tags": payload.category_tags,
        "lat": payload.lat,
        "lon": payload.lon,
        "precomputed_traffic": 0.0,
        "traffic_confidence": "low",
    }
    upsert_spot(spot_id=spot_id, embedding=embedding, metadata=metadata, collection_name=settings.QDRANT_COLLECTION)

    resp = SpotResponse(
        id=spot_id,
        supplier_id=payload.supplier_id,
        title=payload.title,
        description=payload.description,
        category_tags=payload.category_tags,
        lat=payload.lat,
        lon=payload.lon,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        availability=payload.availability,
        created_at=None,
        precomputed_traffic=metadata["precomputed_traffic"],
        traffic_confidence=metadata["traffic_confidence"],
    )
    return resp
