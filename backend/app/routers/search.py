# backend/app/routers/search.py
from fastapi import APIRouter
from ..models.search import SearchRequest, SearchResponse, SearchResultItem
from ..services.search_engine import search_spots

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/semantic", response_model=SearchResponse)
def semantic_search(req: SearchRequest):
    results = search_spots(
        query=req.query,
        user_lat=req.lat,
        user_lon=req.lon,
        top_k=req.top_k or 20,
    )

    items = []
    for r in results[: (req.top_k or 10)]:
        items.append(
            SearchResultItem(
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
        )
    return SearchResponse(query=req.query, results=items)
