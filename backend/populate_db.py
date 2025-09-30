#!/usr/bin/env python3
"""
Script to populate the Qdrant database with sample advertising spots data.
Run this script to add sample data for testing the semantic search functionality.
"""

import sys
import os
import logging
from typing import List, Dict, Any
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vectordb import ensure_collection, upsert_spot
from app.services.embeddings import embed_text
from app.config import settings
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample advertising spots data
SAMPLE_SPOTS = [
    {
        "id": "stadium_1",
        "title": "Wembley Stadium",
        "description": "Iconic football stadium in London, perfect for sports advertising. High footfall during matches and events.",
        "category_tags": ["sports", "stadium", "football", "events", "london"],
        "lat": 51.5560,
        "lon": -0.2795,
        "precomputed_traffic": 8500,
        "traffic_confidence": "high"
    },
    {
        "id": "stadium_2", 
        "title": "Old Trafford",
        "description": "Manchester United's home ground, one of the most famous football stadiums in the world.",
        "category_tags": ["sports", "stadium", "football", "manchester", "premier_league"],
        "lat": 53.4631,
        "lon": -2.2913,
        "precomputed_traffic": 9200,
        "traffic_confidence": "high"
    },
    {
        "id": "shopping_1",
        "title": "Westfield London",
        "description": "Large shopping center in West London with high foot traffic and diverse demographics.",
        "category_tags": ["shopping", "retail", "london", "fashion", "entertainment"],
        "lat": 51.5074,
        "lon": -0.1278,
        "precomputed_traffic": 12000,
        "traffic_confidence": "high"
    },
    {
        "id": "shopping_2",
        "title": "Manchester Arndale",
        "description": "Central Manchester shopping center with excellent transport links and high visitor numbers.",
        "category_tags": ["shopping", "retail", "manchester", "city_center", "transport_hub"],
        "lat": 53.4808,
        "lon": -2.2426,
        "precomputed_traffic": 9800,
        "traffic_confidence": "high"
    },
    {
        "id": "transport_1",
        "title": "King's Cross Station",
        "description": "Major railway station in London with international connections and high daily footfall.",
        "category_tags": ["transport", "station", "london", "international", "commuter"],
        "lat": 51.5308,
        "lon": -0.1238,
        "precomputed_traffic": 15000,
        "traffic_confidence": "high"
    },
    {
        "id": "transport_2",
        "title": "Manchester Piccadilly",
        "description": "Main railway station in Manchester city center with excellent connectivity.",
        "category_tags": ["transport", "station", "manchester", "city_center", "commuter"],
        "lat": 53.4773,
        "lon": -2.2307,
        "precomputed_traffic": 11000,
        "traffic_confidence": "high"
    },
    {
        "id": "university_1",
        "title": "University of Oxford",
        "description": "Historic university with high student and visitor traffic, ideal for educational and cultural advertising.",
        "category_tags": ["education", "university", "oxford", "students", "cultural"],
        "lat": 51.7548,
        "lon": -1.2544,
        "precomputed_traffic": 5000,
        "traffic_confidence": "medium"
    },
    {
        "id": "university_2",
        "title": "University of Cambridge",
        "description": "Prestigious university with significant foot traffic from students, staff, and tourists.",
        "category_tags": ["education", "university", "cambridge", "students", "cultural"],
        "lat": 52.2053,
        "lon": 0.1218,
        "precomputed_traffic": 4500,
        "traffic_confidence": "medium"
    },
    {
        "id": "airport_1",
        "title": "Heathrow Airport Terminal 5",
        "description": "International airport terminal with high passenger traffic and premium advertising opportunities.",
        "category_tags": ["airport", "international", "travel", "london", "premium"],
        "lat": 51.4700,
        "lon": -0.4543,
        "precomputed_traffic": 18000,
        "traffic_confidence": "high"
    },
    {
        "id": "airport_2",
        "title": "Manchester Airport",
        "description": "Major international airport serving the North of England with significant passenger numbers.",
        "category_tags": ["airport", "international", "travel", "manchester", "north"],
        "lat": 53.3536,
        "lon": -2.2748,
        "precomputed_traffic": 14000,
        "traffic_confidence": "high"
    },
    {
        "id": "entertainment_1",
        "title": "O2 Arena London",
        "description": "Major entertainment venue hosting concerts, sports events, and exhibitions with high visitor numbers.",
        "category_tags": ["entertainment", "arena", "concerts", "events", "london"],
        "lat": 51.5029,
        "lon": 0.0032,
        "precomputed_traffic": 8000,
        "traffic_confidence": "high"
    },
    {
        "id": "entertainment_2",
        "title": "Manchester Arena",
        "description": "Large indoor arena in Manchester city center hosting major concerts and events.",
        "category_tags": ["entertainment", "arena", "concerts", "events", "manchester"],
        "lat": 53.4882,
        "lon": -2.2426,
        "precomputed_traffic": 7500,
        "traffic_confidence": "high"
    }
]

def create_spot_embeddings(spots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create embeddings for spot descriptions and titles."""
    logger.info(f"Creating embeddings for {len(spots)} spots")
    
    # Prepare texts for embedding (combine title and description)
    texts = []
    for spot in spots:
        text = f"{spot['title']} {spot['description']}"
        # Add category tags to the text for better semantic matching
        if spot.get('category_tags'):
            text += " " + " ".join(spot['category_tags'])
        texts.append(text)
    
    try:
        embeddings = embed_text(texts, model=settings.EMBEDDING_MODEL)
        logger.info(f"Successfully created {len(embeddings)} embeddings")
        
        # Combine spots with their embeddings
        spots_with_embeddings = []
        for i, spot in enumerate(spots):
            spot_with_embedding = spot.copy()
            spot_with_embedding['embedding'] = embeddings[i]
            spots_with_embeddings.append(spot_with_embedding)
        
        return spots_with_embeddings
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")
        raise

def populate_database():
    """Main function to populate the database with sample data."""
    logger.info("Starting database population")
    
    # Validate required environment variables
    try:
        settings.validate_required_fields()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set the following environment variables:")
        logger.error("  OPENAI_API_KEY=your_openai_api_key_here")
        logger.error("  QDRANT_API_KEY=your_qdrant_api_key_here")
        logger.error("  QDRANT_URL=https://your-cluster-url.qdrant.tech")
        logger.error("Or create a .env file with these variables")
        return False
    
    try:
        # Ensure collection exists
        logger.info("Ensuring collection exists")
        ensure_collection(vector_size=1536)  # OpenAI text-embedding-3-small has 1536 dimensions
        
        # Create embeddings for all spots
        spots_with_embeddings = create_spot_embeddings(SAMPLE_SPOTS)
        
        # Insert spots into Qdrant
        logger.info("Inserting spots into Qdrant")
        for spot in spots_with_embeddings:
            try:
                # Convert string ID to UUID for Qdrant compatibility
                spot_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, spot['id']))
                
                # Prepare metadata (everything except embedding)
                metadata = {k: v for k, v in spot.items() if k not in ['embedding']}
                
                upsert_spot(
                    spot_id=spot_uuid,
                    embedding=spot['embedding'],
                    metadata=metadata
                )
                logger.info(f"Successfully inserted spot: {spot['title']} (UUID: {spot_uuid})")
            except Exception as e:
                logger.error(f"Failed to insert spot {spot['id']}: {e}")
                continue
        
        logger.info("Database population completed successfully!")
        logger.info(f"Inserted {len(spots_with_embeddings)} spots into the collection")
        return True
        
    except Exception as e:
        logger.error(f"Database population failed: {e}")
        return False

if __name__ == "__main__":
    populate_database()
