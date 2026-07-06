from fastapi import APIRouter

from app.schemas.ai import GeneratedRecipe, GenerateRecipeRequest, ImproveRecipeRequest, PantryRequest
from app.services.ai_service import generate_recipe, improve_recipe, recommend_from_pantry

router = APIRouter()


@router.post("/pantry", response_model=GeneratedRecipe)
def pantry(payload: PantryRequest) -> GeneratedRecipe:
    return recommend_from_pantry(payload)


@router.post("/generate", response_model=GeneratedRecipe)
def generate(payload: GenerateRecipeRequest) -> GeneratedRecipe:
    return generate_recipe(payload)


@router.post("/improve", response_model=GeneratedRecipe)
def improve(payload: ImproveRecipeRequest) -> GeneratedRecipe:
    return improve_recipe(payload)

