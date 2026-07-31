from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DietaryRestriction = Literal[
    "vegan",
    "vegetarian",
    "gluten-free",
    "dairy-free",
    "egg-free",
    "nut-free",
    "reduced-sugar",
]


class RecipeIngredient(BaseModel):
    item: str
    amount: str
    notes: str | None = None
    optional: bool = False
    substitutions: list[str] = Field(default_factory=list)


class RecipeStep(BaseModel):
    title: str
    detail: str
    time_minutes: int | None = Field(default=None, ge=0)
    temperature_f: int | None = Field(default=None, ge=0)
    visual_cue: str | None = None
    why_it_matters: str | None = None


class RecipeTiming(BaseModel):
    prep_minutes: int = Field(ge=0)
    bake_minutes: int = Field(ge=0)
    rest_minutes: int = Field(ge=0)
    total_minutes: int = Field(ge=0)


class RecipeValidation(BaseModel):
    detected_restrictions: list[DietaryRestriction] = Field(default_factory=list)
    honored_restrictions: list[DietaryRestriction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0, le=1)


class RecipeQualityScore(BaseModel):
    overall: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    timing_detail: int = Field(ge=0, le=100)
    dietary_safety: int = Field(ge=0, le=100)
    beginner_friendliness: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class TroubleshootingIssue(BaseModel):
    issue: str
    likely_cause: str
    fix_next_time: str
    severity: Literal["low", "medium", "high"] = "medium"


class GeneratedRecipe(BaseModel):
    title: str
    summary: str
    ingredients: list[str]
    detailed_ingredients: list[RecipeIngredient] = Field(default_factory=list)
    instructions: list[RecipeStep]
    baking_time: str
    timing: RecipeTiming | None = None
    difficulty: str
    yield_amount: str = "One home-baking batch"
    oven_temperature_f: int | None = None
    equipment: list[str] = Field(default_factory=list)
    storage: str | None = None
    tips: list[str] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    change_notes: list[str] = Field(default_factory=list)
    validation: RecipeValidation = Field(default_factory=RecipeValidation)
    quality_score: RecipeQualityScore | None = None
    troubleshooting: list[TroubleshootingIssue] = Field(default_factory=list)


class PantryRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    preferences: str | None = None
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=list)
    skill_level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class GenerateRecipeRequest(BaseModel):
    prompt: str = Field(min_length=4)
    dietary_notes: str | None = None
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=list)
    sweetness: Literal["low", "medium", "classic"] = "medium"
    texture: str | None = None
    skill_level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class ImproveRecipeRequest(BaseModel):
    recipe_text: str = Field(min_length=20)
    goal: str = Field(min_length=3)
    dietary_restrictions: list[DietaryRestriction] = Field(default_factory=list)


class TroubleshooterRequest(BaseModel):
    description: str = Field(min_length=4)
    recipe_context: str | None = None
    bake_type: str | None = None


class TroubleshooterResponse(BaseModel):
    summary: str
    likely_issues: list[TroubleshootingIssue]
    next_bake_plan: list[str]
    confidence: float = Field(ge=0, le=1)
