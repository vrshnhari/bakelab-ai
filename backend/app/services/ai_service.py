import json

from openai import OpenAI

from app.config import settings
from app.schemas.ai import (
    GeneratedRecipe,
    GenerateRecipeRequest,
    ImproveRecipeRequest,
    PantryRequest,
    RecipeStep,
)


SYSTEM_PROMPT = """
You are BakeLab AI, a practical baking assistant for home bakers.
Return accurate, food-safe baking guidance. Prefer clear measurements,
realistic temperatures, and beginner-friendly steps. Output valid JSON only.
"""


def _mock_recipe(title: str, summary: str, missing_items: list[str] | None = None) -> GeneratedRecipe:
    return GeneratedRecipe(
        title=title,
        summary=summary,
        ingredients=[
            "1 1/2 cups all-purpose flour",
            "1/2 cup unsalted butter, softened",
            "2/3 cup sugar",
            "1 large egg",
            "1 tsp vanilla extract",
            "1 tsp baking powder",
            "1/4 tsp fine salt",
        ],
        instructions=[
            RecipeStep(title="Prep", detail="Heat oven to 350 F and line a baking sheet with parchment."),
            RecipeStep(title="Mix", detail="Cream butter and sugar, then beat in egg and vanilla until glossy."),
            RecipeStep(title="Combine", detail="Fold in dry ingredients just until no flour streaks remain."),
            RecipeStep(title="Bake", detail="Portion dough and bake for 10 to 12 minutes until edges are set."),
        ],
        baking_time="25 minutes total",
        difficulty="Easy",
        tips=[
            "Pull the bake when the center still looks slightly soft for a tender texture.",
            "Chill dough for 20 minutes if the kitchen is warm.",
        ],
        missing_items=missing_items or [],
    )


def _client() -> OpenAI | None:
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _json_recipe(user_prompt: str) -> GeneratedRecipe:
    client = _client()
    if client is None:
        return _mock_recipe(
            "Vanilla Butter Cookies",
            "A dependable starter recipe returned in mock mode. Add OPENAI_API_KEY for live AI results.",
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"{user_prompt}\n\n"
                    "Return JSON with keys: title, summary, ingredients, instructions, "
                    "baking_time, difficulty, tips, missing_items, change_notes. "
                    "instructions must be an array of objects with title and detail."
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return GeneratedRecipe.model_validate(json.loads(content))


def recommend_from_pantry(payload: PantryRequest) -> GeneratedRecipe:
    if _client() is None:
        return _mock_recipe(
            "Pantry Jam Crumble Bars",
            "A buttery bar cookie idea built around common pantry staples and flexible fruit filling.",
            missing_items=["fruit jam or preserves", "rolled oats"],
        )

    ingredients = ", ".join(payload.ingredients)
    return _json_recipe(
        "Create a baking recipe using these ingredients where possible: "
        f"{ingredients}. Preferences: {payload.preferences or 'none'}. "
        "Highlight missing items that would improve the bake."
    )


def generate_recipe(payload: GenerateRecipeRequest) -> GeneratedRecipe:
    return _json_recipe(
        f"Generate a complete baking recipe for: {payload.prompt}. "
        f"Dietary notes: {payload.dietary_notes or 'none'}."
    )


def improve_recipe(payload: ImproveRecipeRequest) -> GeneratedRecipe:
    if _client() is None:
        recipe = _mock_recipe(
            "Improved Chocolate Snack Cake",
            "A mock improved recipe showing how BakeLab explains ingredient and process changes.",
        )
        recipe.change_notes = [
            f"Adjusted the recipe toward this goal: {payload.goal}.",
            "Reduced sugar slightly and added salt to keep flavor balanced.",
            "Clarified mixing steps to avoid a dense crumb.",
        ]
        return recipe

    return _json_recipe(
        "Improve this baking recipe. Explain each meaningful change in change_notes. "
        f"Goal: {payload.goal}\n\nRecipe:\n{payload.recipe_text}"
    )

