# backend/app/services/embeddings.py
import os
from typing import List
import openai
from ..config import settings
import logging

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY


def embed_text(texts: List[str], model: str = None) -> List[List[float]]:
    """
    Convert a list of texts to embeddings using OpenAI embeddings.
    Returns list of vector embeddings (floats).
    """
    model = model or settings.EMBEDDING_MODEL
    logger.info(f"Creating embeddings for {len(texts)} texts using model '{model}'")
    logger.debug(f"Texts to embed: {texts}")
    
    try:
        # OpenAI's Python SDK returns embedding per input
        resp = openai.Embedding.create(model=model, input=texts)
        embeddings = [item["embedding"] for item in resp["data"]]
        logger.info(f"Successfully created {len(embeddings)} embeddings with dimension {len(embeddings[0]) if embeddings else 0}")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")
        raise
