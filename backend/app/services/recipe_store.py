from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

from app import database
from app.models import RecipeRecord
from app.schemas.recipes import SavedRecipe, SavedRecipeCreate, SavedRecipeUpdate


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "recipes.json"


def _use_database() -> bool:
    return database.database_available()


def _record_to_schema(record: RecipeRecord) -> SavedRecipe:
    return SavedRecipe(
        id=record.id,
        title=record.title,
        folder=record.folder,
        tags=record.tags or [],
        recipe=record.recipe,
        baking_journal=record.baking_journal,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _filter_recipes(values: list[SavedRecipe], query: str | None = None, folder: str | None = None) -> list[SavedRecipe]:
    if folder:
        values = [recipe for recipe in values if recipe.folder.lower() == folder.lower()]
    if query:
        needle = query.lower()
        values = [
            recipe
            for recipe in values
            if needle in recipe.title.lower()
            or needle in recipe.recipe.summary.lower()
            or any(needle in tag.lower() for tag in recipe.tags)
        ]
    return sorted(values, key=lambda recipe: recipe.updated_at, reverse=True)


def _load() -> dict[str, SavedRecipe]:
    if not DATA_FILE.exists():
        return {}
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {item["id"]: SavedRecipe.model_validate(item) for item in raw}


def _save(recipes: dict[str, SavedRecipe]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = [recipe.model_dump(mode="json") for recipe in recipes.values()]
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def list_recipes(query: str | None = None, folder: str | None = None) -> list[SavedRecipe]:
    if _use_database():
        with database.SessionLocal() as session:  # type: ignore[misc]
            statement = select(RecipeRecord)
            records = session.scalars(statement).all()
            values = [_record_to_schema(record) for record in records]
            return _filter_recipes(values, query=query, folder=folder)

    recipes = _load()
    return _filter_recipes(list(recipes.values()), query=query, folder=folder)


def get_recipe(recipe_id: str) -> SavedRecipe | None:
    if _use_database():
        with database.SessionLocal() as session:  # type: ignore[misc]
            record = session.get(RecipeRecord, recipe_id)
            return _record_to_schema(record) if record else None

    return _load().get(recipe_id)


def create_recipe(payload: SavedRecipeCreate) -> SavedRecipe:
    if _use_database():
        with database.SessionLocal() as session:  # type: ignore[misc]
            now = datetime.now(timezone.utc)
            record = RecipeRecord(
                id=str(uuid4()),
                title=payload.title,
                folder=payload.folder,
                tags=payload.tags,
                recipe=payload.recipe.model_dump(mode="json"),
                baking_journal=payload.baking_journal.model_dump(mode="json") if payload.baking_journal else None,
                notes=payload.notes,
                created_at=now,
                updated_at=now,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return _record_to_schema(record)

    recipes = _load()
    now = datetime.now(timezone.utc)
    recipe = SavedRecipe(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    recipes[recipe.id] = recipe
    _save(recipes)
    return recipe


def update_recipe(recipe_id: str, payload: SavedRecipeUpdate) -> SavedRecipe | None:
    if _use_database():
        with database.SessionLocal() as session:  # type: ignore[misc]
            record = session.get(RecipeRecord, recipe_id)
            if record is None:
                return None
            updates = payload.model_dump(exclude_unset=True)
            for key, value in updates.items():
                if key == "baking_journal" and value is not None:
                    setattr(record, key, payload.baking_journal.model_dump(mode="json") if payload.baking_journal else None)
                else:
                    setattr(record, key, value)
            record.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(record)
            return _record_to_schema(record)

    recipes = _load()
    recipe = recipes.get(recipe_id)
    if recipe is None:
        return None
    updates = payload.model_dump(exclude_unset=True)
    updated = recipe.model_copy(update={**updates, "updated_at": datetime.now(timezone.utc)})
    recipes[recipe_id] = updated
    _save(recipes)
    return updated


def delete_recipe(recipe_id: str) -> bool:
    if _use_database():
        with database.SessionLocal() as session:  # type: ignore[misc]
            record = session.get(RecipeRecord, recipe_id)
            if record is None:
                return False
            session.delete(record)
            session.commit()
            return True

    recipes = _load()
    if recipe_id not in recipes:
        return False
    del recipes[recipe_id]
    _save(recipes)
    return True
