# Semantic Search Recommendation System - Setup Guide

## Overview
This is a semantic search recommendation system that uses OpenAI embeddings and Qdrant vector database to provide intelligent advertising spot recommendations based on natural language queries.

## Features
- **Semantic Search**: Uses OpenAI embeddings to understand natural language queries
- **Geographic Filtering**: Considers user location for distance-based scoring
- **Traffic Estimation**: Incorporates traffic data for better recommendations
- **Comprehensive Logging**: Detailed logging throughout the system for debugging
- **Exception Handling**: Robust error handling in all components

## Prerequisites
- Python 3.10+
- OpenAI API key
- Qdrant Cloud account and API key

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-small

# Qdrant Configuration
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_COLLECTION=semantic_spots

# Backend Configuration
HOST=0.0.0.0
PORT=8000
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Populate Database
Run the database population script to add sample data:

```bash
cd backend
python populate_db.py
```

This will create 12 sample advertising spots including:
- Football stadiums (Wembley, Old Trafford)
- Shopping centers (Westfield London, Manchester Arndale)
- Transport hubs (King's Cross, Manchester Piccadilly)
- Universities (Oxford, Cambridge)
- Airports (Heathrow, Manchester)
- Entertainment venues (O2 Arena, Manchester Arena)

### 4. Start the Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Start the Frontend
In a new terminal:
```bash
cd frontend
streamlit run streamlit_app.py
```

## Testing the System

### 1. Test Logging
```bash
cd backend
python test_logging.py
```

### 2. Test API Endpoints
The API will be available at `http://localhost:8000`

- **Health Check**: `GET /`
- **Search**: `POST /search/semantic`

Example search request:
```json
{
  "query": "I want to advertise a football kit near stadiums",
  "lat": 51.5074,
  "lon": -0.1278,
  "top_k": 10
}
```

### 3. Test Frontend
Open `http://localhost:8501` in your browser and try queries like:
- "I want to advertise a football kit near stadiums"
- "Best place for luxury brand advertising in London"
- "Shopping center advertising for fashion brand"

## Logging and Debugging

The system includes comprehensive logging at multiple levels:

- **INFO**: General flow information
- **DEBUG**: Detailed processing information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors

Logs are written to both console and `app.log` file.

### Key Log Points:
1. **Search Request**: Query received with parameters
2. **Embedding Creation**: OpenAI API calls and results
3. **Vector Search**: Qdrant database queries and results
4. **Scoring**: Geographic and traffic scoring calculations
5. **Results**: Final ranked results

## Troubleshooting

### Common Issues:

1. **"No results found"**
   - Check if database is populated: run `python populate_db.py`
   - Verify Qdrant connection and API key
   - Check logs for vector search errors

2. **Environment variable errors**
   - Ensure `.env` file exists with all required variables
   - Check variable names and values

3. **OpenAI API errors**
   - Verify API key is valid and has credits
   - Check rate limits

4. **Qdrant connection errors**
   - Verify URL and API key
   - Check network connectivity

### Debug Mode:
Set logging level to DEBUG for more detailed information:
```python
logging.basicConfig(level=logging.DEBUG)
```

## System Architecture

```
Frontend (Streamlit) 
    ↓ HTTP POST
Backend (FastAPI)
    ↓
Search Router
    ↓
Search Engine
    ↓
Embeddings Service (OpenAI) + Vector DB (Qdrant)
    ↓
Scoring & Ranking
    ↓
Results
```

## File Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app with logging config
│   ├── config.py            # Settings with validation
│   ├── routers/
│   │   └── search.py        # Search endpoints with logging
│   ├── services/
│   │   ├── embeddings.py    # OpenAI integration with logging
│   │   ├── search_engine.py # Main search logic with logging
│   │   └── vectordb.py      # Qdrant integration with logging
│   ├── models/
│   │   └── search.py        # Pydantic models
│   └── utils/
│       ├── geo.py           # Geographic calculations
│       └── scoring.py       # Scoring algorithms
├── populate_db.py           # Database population script
└── test_logging.py          # Logging test script

frontend/
└── streamlit_app.py         # Streamlit UI
```

## Next Steps
1. Set up your environment variables
2. Run the database population script
3. Start the backend and frontend
4. Test with sample queries
5. Check logs for any issues
