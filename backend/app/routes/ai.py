from fastapi import APIRouter, Depends

from app.schemas.ai import (
    GeneratedRecipe,
    GenerateRecipeRequest,
    ImproveRecipeRequest,
    PantryRequest,
    TroubleshooterRequest,
    TroubleshooterResponse,
)
from app.services.ai_service import generate_recipe, improve_recipe, recommend_from_pantry, troubleshoot_bake
from app.services.rate_limiter import rate_limit_ai

router = APIRouter(dependencies=[Depends(rate_limit_ai)])


@router.post("/pantry", response_model=GeneratedRecipe)
def pantry(payload: PantryRequest) -> GeneratedRecipe:
    return recommend_from_pantry(payload)


@router.post("/generate", response_model=GeneratedRecipe)
def generate(payload: GenerateRecipeRequest) -> GeneratedRecipe:
    return generate_recipe(payload)


@router.post("/improve", response_model=GeneratedRecipe)
def improve(payload: ImproveRecipeRequest) -> GeneratedRecipe:
    return improve_recipe(payload)


@router.post("/troubleshoot", response_model=TroubleshooterResponse)
def troubleshoot(payload: TroubleshooterRequest) -> TroubleshooterResponse:
    return troubleshoot_bake(payload)
