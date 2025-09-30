# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import spots, search
from .config import settings
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Semantic Ads Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo - allow all; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spots.router)
app.include_router(search.router)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"ok": True, "message": "Semantic Ads Demo - backend running"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Semantic Ads Demo backend")
    logger.info(f"Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"Qdrant Collection: {settings.QDRANT_COLLECTION}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Semantic Ads Demo backend")
