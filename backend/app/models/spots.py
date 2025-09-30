# backend/app/models/spots.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class SpotCreate(BaseModel):
    supplier_id: str
    title: str
    description: Optional[str] = None
    category_tags: Optional[List[str]] = []
    lat: float
    lon: float
    width_cm: Optional[int] = None
    height_cm: Optional[int] = None
    availability: Optional[dict] = Field(default_factory=dict)  # simple calendar or JSON

class SpotInDB(SpotCreate):
    id: str
    created_at: Optional[str] = None

class SpotResponse(SpotInDB):
    precomputed_traffic: Optional[float] = None
    traffic_confidence: Optional[str] = None
