# backend/app/routers/search.py
from fastapi import APIRouter, HTTPException
from ..models.search import SearchRequest, SearchResponse, SearchResultItem
from ..services.search_engine import search_spots
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.post("/semantic", response_model=SearchResponse)
def semantic_search(req: SearchRequest):
    logger.info(f"Received search request: query='{req.query}', lat={req.lat}, lon={req.lon}, top_k={req.top_k}")
    
    try:
        results = search_spots(
            query=req.query,
            user_lat=req.lat,
            user_lon=req.lon,
            top_k=req.top_k or 20,
        )
        logger.info(f"Search engine returned {len(results)} results")

        items = []
        limit = req.top_k or 10
        for i, r in enumerate(results[:limit]):
            try:
                item = SearchResultItem(
                    id=r["id"],
                    title=r["title"],
                    description=r["description"],
                    category_tags=r["category_tags"] or [],
                    lat=r["lat"],
                    lon=r["lon"],
                    distance_km=r["distance_km"] or -1.0,
                    semantic_score=r["semantic_score"],
                    traffic_estimate=r["traffic_estimate"] or 0.0,
                    traffic_confidence=r["traffic_confidence"],
                    final_score=r["final_score"],
                )
                items.append(item)
                logger.debug(f"Created result item {i+1}: {item.title} (score: {item.final_score:.4f})")
            except Exception as item_error:
                logger.error(f"Failed to create result item {i+1}: {item_error}")
                continue
        
        logger.info(f"Returning {len(items)} search results")
        return SearchResponse(query=req.query, results=items)
        
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
