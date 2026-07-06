from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.recipes import SavedRecipe, SavedRecipeCreate

router = APIRouter()

_RECIPES: dict[str, SavedRecipe] = {}


@router.get("", response_model=list[SavedRecipe])
def list_recipes() -> list[SavedRecipe]:
    return sorted(_RECIPES.values(), key=lambda recipe: recipe.updated_at, reverse=True)


@router.post("", response_model=SavedRecipe)
def create_recipe(payload: SavedRecipeCreate) -> SavedRecipe:
    now = datetime.now(timezone.utc)
    recipe = SavedRecipe(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    _RECIPES[recipe.id] = recipe
    return recipe

