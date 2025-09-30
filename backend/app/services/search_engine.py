# backend/app/services/search_engine.py
from typing import List, Dict, Any
from ..services.embeddings import embed_text
from ..services.vectordb import search_vectors
from ..utils.geo import haversine_km
from ..utils.scoring import geo_score, normalize, final_score
from ..config import settings


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
    # 1. embed
    q_emb = embed_text([query], model=settings.EMBEDDING_MODEL)[0]

    # 2. vector search (returns payloads containing spot metadata incl lat/lon)
    vec_results = search_vectors(query_vector=q_emb, top_k=top_k)

    processed = []
    # For traffic normalization choose a simple expected range
    TRAFFIC_MIN = 0.0
    TRAFFIC_MAX = 10000.0  # demo scale (impressions/day)

    for r in vec_results:
        payload = r.get("payload", {})
        meta_lat = payload.get("lat")
        meta_lon = payload.get("lon")
        distance = None
        geo_s = 0.0
        if user_lat is not None and user_lon is not None and meta_lat is not None and meta_lon is not None:
            distance = haversine_km(user_lat, user_lon, float(meta_lat), float(meta_lon))
            geo_s = geo_score(distance)
        traffic_est = payload.get("precomputed_traffic", 0.0) or 0.0
        traffic_norm = normalize(traffic_est, TRAFFIC_MIN, TRAFFIC_MAX)
        sem_score = r.get("score", 0.0)
        fscore = final_score(semantic=sem_score, geo=geo_s, traffic=traffic_norm)
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
    return processed
