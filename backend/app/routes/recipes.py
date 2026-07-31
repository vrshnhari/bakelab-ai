from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from app.schemas.recipes import SavedRecipe, SavedRecipeCreate, SavedRecipeUpdate
from app.services import recipe_store

router = APIRouter()


@router.get("", response_model=list[SavedRecipe])
def list_recipes(
    query: str | None = Query(default=None),
    folder: str | None = Query(default=None),
) -> list[SavedRecipe]:
    return recipe_store.list_recipes(query=query, folder=folder)


@router.get("/{recipe_id}", response_model=SavedRecipe)
def get_recipe(recipe_id: str) -> SavedRecipe:
    recipe = recipe_store.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("", response_model=SavedRecipe)
def create_recipe(payload: SavedRecipeCreate) -> SavedRecipe:
    return recipe_store.create_recipe(payload)


@router.patch("/{recipe_id}", response_model=SavedRecipe)
def update_recipe(recipe_id: str, payload: SavedRecipeUpdate) -> SavedRecipe:
    recipe = recipe_store.update_recipe(recipe_id, payload)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: str) -> Response:
    deleted = recipe_store.delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Response(status_code=204)
