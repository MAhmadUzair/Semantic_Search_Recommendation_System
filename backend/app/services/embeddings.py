# backend/app/services/embeddings.py
import os
from typing import List
import openai
from ..config import settings

openai.api_key = settings.OPENAI_API_KEY


def embed_text(texts: List[str], model: str = None) -> List[List[float]]:
    """
    Convert a list of texts to embeddings using OpenAI embeddings.
    Returns list of vector embeddings (floats).
    """
    model = model or settings.EMBEDDING_MODEL
    # OpenAI's Python SDK returns embedding per input
    resp = openai.Embedding.create(model=model, input=texts)
    embeddings = [item["embedding"] for item in resp["data"]]
    return embeddings
