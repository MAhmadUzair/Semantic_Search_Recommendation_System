# backend/app/models/search.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class SearchRequest(BaseModel):
    query: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_km: Optional[float] = 25.0
    top_k: Optional[int] = 10
    filters: Optional[Dict] = None


class SearchResultItem(BaseModel):
    id: str
    title: str
    description: str | None
    category_tags: list | None
    lat: float
    lon: float
    distance_km: float
    semantic_score: float
    traffic_estimate: float | None
    traffic_confidence: str | None
    final_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
