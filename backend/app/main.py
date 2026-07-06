from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import ai, recipes

app = FastAPI(
    title="BakeLab AI API",
    description="AI-powered baking assistant backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

