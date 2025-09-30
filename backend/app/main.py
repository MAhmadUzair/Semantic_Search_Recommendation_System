# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import spots, search
from .config import settings

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
    return {"ok": True, "message": "Semantic Ads Demo - backend running"}
