# backend/app/services/search_engine.py
from typing import List, Dict, Any
from ..services.embeddings import embed_text
from ..services.vectordb import search_vectors
from ..utils.geo import haversine_km
from ..utils.scoring import geo_score, normalize, final_score
from ..config import settings
import logging

logger = logging.getLogger(__name__)


def search_spots(
    query: str,
    user_lat: float | None = None,
    user_lon: float | None = None,
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    """
    High-level search flow:
      - embed query
      - query vector DB for top_k semantic candidates
      - compute distance and ranking signals if lat/lon present
      - compute final score and return sorted list
    """
    logger.info(f"Starting search for query: '{query}', user_location=({user_lat}, {user_lon}), top_k={top_k}")
    
    try:
        # 1. embed
        logger.info("Step 1: Creating query embedding")
        q_emb = embed_text([query], model=settings.EMBEDDING_MODEL)[0]
        logger.info(f"Query embedding created with dimension {len(q_emb)}")

        # 2. vector search (returns payloads containing spot metadata incl lat/lon)
        logger.info("Step 2: Searching vector database")
        vec_results = search_vectors(query_vector=q_emb, top_k=top_k)
        logger.info(f"Vector search returned {len(vec_results)} results")

        processed = []
        # For traffic normalization choose a simple expected range
        TRAFFIC_MIN = 0.0
        TRAFFIC_MAX = 10000.0  # demo scale (impressions/day)

        logger.info("Step 3: Processing and scoring results")
        for i, r in enumerate(vec_results):
            payload = r.get("payload", {})
            meta_lat = payload.get("lat")
            meta_lon = payload.get("lon")
            distance = None
            geo_s = 0.0
            
            logger.debug(f"Processing result {i+1}: id={r['id']}, payload_keys={list(payload.keys())}")
            
            if user_lat is not None and user_lon is not None and meta_lat is not None and meta_lon is not None:
                distance = haversine_km(user_lat, user_lon, float(meta_lat), float(meta_lon))
                geo_s = geo_score(distance)
                logger.debug(f"  Distance: {distance:.2f}km, geo_score: {geo_s:.4f}")
            else:
                logger.debug(f"  No location data - user=({user_lat}, {user_lon}), spot=({meta_lat}, {meta_lon})")
                
            traffic_est = payload.get("precomputed_traffic", 0.0) or 0.0
            traffic_norm = normalize(traffic_est, TRAFFIC_MIN, TRAFFIC_MAX)
            sem_score = r.get("score", 0.0)
            fscore = final_score(semantic=sem_score, geo=geo_s, traffic=traffic_norm)
            
            logger.debug(f"  Scores - semantic: {sem_score:.4f}, geo: {geo_s:.4f}, traffic: {traffic_norm:.4f}, final: {fscore:.4f}")
            
            processed.append(
                {
                    "id": r["id"],
                    "title": payload.get("title"),
                    "description": payload.get("description"),
                    "category_tags": payload.get("category_tags"),
                    "lat": float(meta_lat) if meta_lat is not None else None,
                    "lon": float(meta_lon) if meta_lon is not None else None,
                    "distance_km": distance,
                    "semantic_score": sem_score,
                    "traffic_estimate": traffic_est,
                    "traffic_confidence": payload.get("traffic_confidence", "low"),
                    "final_score": fscore,
                }
            )

        # sort by final_score desc
        processed = sorted(processed, key=lambda x: x["final_score"], reverse=True)
        logger.info(f"Step 4: Final results - {len(processed)} spots sorted by final score")
        logger.debug(f"Top 3 final scores: {[p['final_score'] for p in processed[:3]]}")
        return processed
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise
