from pydantic import BaseModel, Field


class RecipeStep(BaseModel):
    title: str
    detail: str


class GeneratedRecipe(BaseModel):
    title: str
    summary: str
    ingredients: list[str]
    instructions: list[RecipeStep]
    baking_time: str
    difficulty: str
    tips: list[str] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    change_notes: list[str] = Field(default_factory=list)


class PantryRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    preferences: str | None = None


class GenerateRecipeRequest(BaseModel):
    prompt: str = Field(min_length=4)
    dietary_notes: str | None = None


class ImproveRecipeRequest(BaseModel):
    recipe_text: str = Field(min_length=20)
    goal: str = Field(min_length=3)

