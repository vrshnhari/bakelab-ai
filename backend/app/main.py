from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import database_available, init_db
from app.routes import ai, recipes

app = FastAPI(
    title="BakeLab AI API",
    description="AI-powered baking assistant backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    storage = "postgresql" if database_available() else "json"
    return {"status": "ok", "storage": storage}
