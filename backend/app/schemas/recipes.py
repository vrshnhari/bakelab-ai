from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.ai import GeneratedRecipe


class SavedRecipeCreate(BaseModel):
    title: str = Field(min_length=1)
    folder: str = "Favorites"
    recipe: GeneratedRecipe
    notes: str | None = None


class SavedRecipe(SavedRecipeCreate):
    id: str
    created_at: datetime
    updated_at: datetime

