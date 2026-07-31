from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.ai import GeneratedRecipe


class BakingJournal(BaseModel):
    checked_ingredients: list[str] = Field(default_factory=list)
    completed_steps: list[int] = Field(default_factory=list)
    step_notes: dict[str, str] = Field(default_factory=dict)
    reflection: str = ""


class SavedRecipeCreate(BaseModel):
    title: str = Field(min_length=1)
    folder: str = "Favorites"
    recipe: GeneratedRecipe
    tags: list[str] = Field(default_factory=list)
    baking_journal: BakingJournal | None = None
    notes: str | None = None


class SavedRecipeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    folder: str | None = None
    tags: list[str] | None = None
    baking_journal: BakingJournal | None = None
    notes: str | None = None


class SavedRecipe(SavedRecipeCreate):
    id: str
    created_at: datetime
    updated_at: datetime
