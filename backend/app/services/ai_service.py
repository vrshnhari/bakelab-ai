from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from app.config import settings
from app.schemas.ai import (
    GeneratedRecipe,
    GenerateRecipeRequest,
    ImproveRecipeRequest,
    PantryRequest,
    RecipeIngredient,
    RecipeStep,
    RecipeTiming,
    TroubleshooterRequest,
    TroubleshooterResponse,
    TroubleshootingIssue,
)
from app.services.dietary import detect_restrictions, merge_restrictions, validate_recipe
from app.services.recipe_quality import score_recipe


SYSTEM_PROMPT = """
You are BakeLab AI, a precise baking assistant for home bakers.
You must produce safe, practical baking recipes with real measurements,
temperatures, timing, texture cues, and explanations.

Hard rules:
- Honor dietary restrictions exactly.
- If vegan, do not use eggs, dairy milk, butter, cream, honey, gelatin, or other animal products.
- If gluten-free, avoid wheat flour unless it is explicitly gluten-free.
- Explain substitutions and why each important step matters.
- Prefer realistic home equipment and beginner-safe instructions.
- Return structured JSON only.
"""


def _client() -> Any | None:
    if not settings.openai_api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def _recipe_json_schema() -> dict[str, Any]:
    schema = GeneratedRecipe.model_json_schema()
    schema["additionalProperties"] = False
    return schema


def _json_from_response(response: Any) -> dict[str, Any]:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return json.loads(output_text)

    # Compatibility fallback for SDK versions that expose raw output blocks.
    output = getattr(response, "output", None) or []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                return json.loads(text)
    raise ValueError("OpenAI response did not include JSON text.")


def _call_openai(user_prompt: str) -> GeneratedRecipe | None:
    client = _client()
    if client is None:
        return None

    try:
        response = client.responses.create(
            model=settings.openai_model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "generated_recipe",
                    "schema": _recipe_json_schema(),
                    "strict": True,
                }
            },
        )
        return GeneratedRecipe.model_validate(_json_from_response(response))
    except Exception:
        # Keep the app demoable if the OpenAI SDK/model/schema combination changes.
        return None


def _flag_text(restrictions: list[str]) -> str:
    if not restrictions:
        return "classic"
    return ", ".join(restrictions)


def _fallback_recipe(
    title: str,
    summary: str,
    restrictions: list[str],
    missing_items: list[str] | None = None,
    change_notes: list[str] | None = None,
) -> GeneratedRecipe:
    vegan = "vegan" in restrictions or "egg-free" in restrictions or "dairy-free" in restrictions
    gluten_free = "gluten-free" in restrictions
    reduced_sugar = "reduced-sugar" in restrictions

    flour = "1 cup gluten-free 1:1 baking flour" if gluten_free else "1 cup all-purpose flour"
    fat = "1/3 cup neutral oil or melted vegan butter" if vegan else "1/3 cup melted unsalted butter"
    milk = "1/2 cup oat milk or soy milk" if vegan else "1/2 cup whole milk"
    binder = (
        "1 flax binder: 1 tbsp ground flaxseed mixed with 3 tbsp warm water"
        if vegan
        else "1 large egg, room temperature"
    )
    sugar = "1/2 cup brown sugar" if reduced_sugar else "2/3 cup brown sugar"

    detailed = [
        RecipeIngredient(item="Flour", amount=flour, notes="Base structure", substitutions=["oat flour blend"] if gluten_free else []),
        RecipeIngredient(item="Cocoa powder", amount="1/3 cup", notes="Use unsweetened cocoa for balance"),
        RecipeIngredient(item="Brown sugar", amount=sugar, notes="Keeps crumb moist"),
        RecipeIngredient(item="Baking powder", amount="1 tsp"),
        RecipeIngredient(item="Baking soda", amount="1/4 tsp"),
        RecipeIngredient(item="Fine salt", amount="1/2 tsp"),
        RecipeIngredient(item="Fat", amount=fat, notes="Adds tenderness"),
        RecipeIngredient(item="Binder", amount=binder, notes="Holds the crumb together"),
        RecipeIngredient(item="Milk", amount=milk, notes="Room temperature blends best"),
        RecipeIngredient(item="Vanilla extract", amount="1 tsp"),
        RecipeIngredient(item="Dark chocolate", amount="1/3 cup chopped", optional=True),
    ]
    generic_items = {"fat", "binder", "milk"}
    ingredients = []
    for ingredient in detailed:
        item_key = ingredient.item.lower().split()[0]
        if item_key in ingredient.amount.lower() or ingredient.item.lower() in generic_items:
            ingredients.append(ingredient.amount)
        else:
            ingredients.append(f"{ingredient.amount} {ingredient.item.lower()}")

    steps = [
        RecipeStep(
            title="Preheat and prepare pan",
            detail="Heat oven to 350 F. Line an 8-inch square pan with parchment, leaving two overhanging sides for easy lifting.",
            time_minutes=8,
            temperature_f=350,
            visual_cue="Oven is fully preheated and pan is evenly lined.",
            why_it_matters="Batter begins reacting once mixed, so the oven needs to be ready first.",
        ),
        RecipeStep(
            title="Prepare binder",
            detail=(
                "Mix ground flaxseed with warm water and rest 10 minutes until glossy and gel-like."
                if vegan
                else "Warm the egg in a bowl of warm tap water for 5 minutes if it is cold."
            ),
            time_minutes=10 if vegan else 5,
            visual_cue="Binder should look smooth and cohesive.",
            why_it_matters="A properly prepared binder prevents a crumbly cake.",
        ),
        RecipeStep(
            title="Whisk dry ingredients",
            detail="Whisk flour, cocoa, sugar, leaveners, and salt for 30 seconds, breaking up cocoa clumps.",
            time_minutes=3,
            visual_cue="Mixture is one even cocoa color with no pale flour pockets.",
            why_it_matters="Even leavener distribution prevents tunneling and uneven rise.",
        ),
        RecipeStep(
            title="Combine wet ingredients",
            detail=f"Whisk {fat}, binder, {milk}, and vanilla until glossy and mostly uniform.",
            time_minutes=2,
            visual_cue="Wet mixture looks satiny, not separated.",
            why_it_matters="Smooth wet ingredients mix faster, reducing risk of overmixing.",
        ),
        RecipeStep(
            title="Fold batter gently",
            detail="Pour wet into dry and fold just until the final flour streak disappears. Fold in chopped chocolate if using.",
            time_minutes=2,
            visual_cue="Batter is thick and glossy with a few tiny lumps.",
            why_it_matters="Stopping early keeps the cake tender instead of tough.",
        ),
        RecipeStep(
            title="Bake and check doneness",
            detail="Spread batter evenly and bake for 22 to 27 minutes. Start checking at 22 minutes.",
            time_minutes=27,
            temperature_f=350,
            visual_cue="Edges are set; center barely wobbles; toothpick has moist crumbs, not wet batter.",
            why_it_matters="Moist crumbs mean fudgy. A clean toothpick can mean overbaked.",
        ),
        RecipeStep(
            title="Cool before slicing",
            detail="Cool 15 minutes in the pan, then lift out and cool 10 more minutes before slicing.",
            time_minutes=25,
            visual_cue="Cake is warm, not hot, and slices cleanly.",
            why_it_matters="Cooling lets starches set so the center does not collapse.",
        ),
    ]

    recipe = GeneratedRecipe(
        title=title,
        summary=summary,
        ingredients=ingredients,
        detailed_ingredients=detailed,
        instructions=steps,
        baking_time="22 to 27 minutes bake; about 65 minutes total",
        timing=RecipeTiming(prep_minutes=18, bake_minutes=27, rest_minutes=25, total_minutes=70),
        difficulty="Easy",
        yield_amount="9 squares",
        oven_temperature_f=350,
        equipment=["8-inch square pan", "parchment paper", "2 mixing bowls", "whisk", "rubber spatula"],
        storage="Store covered at room temperature for 2 days or refrigerate for 5 days.",
        tips=[
            "Measure flour by spooning into the cup and leveling, not scooping.",
            "Rotate the pan after 16 minutes if your oven browns unevenly.",
            "For cleaner slices, chill 20 minutes after cooling.",
        ],
        missing_items=missing_items or [],
        change_notes=change_notes or [],
        troubleshooting=[
            TroubleshootingIssue(
                issue="Dense center",
                likely_cause="Batter was overmixed or sliced while hot.",
                fix_next_time="Fold only until combined and cool before slicing.",
                severity="medium",
            ),
            TroubleshootingIssue(
                issue="Dry edges",
                likely_cause="Baked too long or pan was dark metal.",
                fix_next_time="Check 3 minutes earlier and use moist-crumb toothpick cue.",
                severity="low",
            ),
        ],
    )
    return score_recipe(validate_recipe(recipe, restrictions))  # type: ignore[arg-type]


def _finalize(recipe: GeneratedRecipe, restrictions: list[str]) -> GeneratedRecipe:
    return score_recipe(validate_recipe(recipe, restrictions))  # type: ignore[arg-type]


def recommend_from_pantry(payload: PantryRequest) -> GeneratedRecipe:
    detected = detect_restrictions(payload.preferences, " ".join(payload.ingredients))
    restrictions = merge_restrictions(payload.dietary_restrictions, detected)
    ingredients = ", ".join(payload.ingredients)
    prompt = (
        "Create a detailed baking recipe from pantry ingredients.\n"
        f"Available ingredients: {ingredients}\n"
        f"Preferences: {payload.preferences or 'none'}\n"
        f"Restrictions: {_flag_text(restrictions)}\n"
        f"Skill level: {payload.skill_level}\n"
        "Include missing useful items, exact timing, equipment, visual cues, and substitution notes."
    )
    recipe = _call_openai(prompt)
    if recipe:
        return _finalize(recipe, restrictions)

    missing = []
    pantry_text = ingredients.lower()
    if "cocoa" not in pantry_text and "chocolate" not in pantry_text:
        missing.append("cocoa powder or dark chocolate")
    if "vegan" in restrictions and "flax" not in pantry_text and "chia" not in pantry_text:
        missing.append("ground flaxseed or chia seed binder")
    return _fallback_recipe(
        "Pantry Cocoa Snack Cake",
        f"A detailed pantry bake built around {ingredients}, adapted for {_flag_text(restrictions)}.",
        restrictions,
        missing_items=missing,
    )


def generate_recipe(payload: GenerateRecipeRequest) -> GeneratedRecipe:
    detected = detect_restrictions(payload.prompt, payload.dietary_notes, payload.texture)
    restrictions = merge_restrictions(payload.dietary_restrictions, detected)
    if payload.sweetness == "low" and "reduced-sugar" not in restrictions:
        restrictions.append("reduced-sugar")  # type: ignore[arg-type]
    prompt = (
        "Generate a portfolio-quality baking recipe.\n"
        f"User request: {payload.prompt}\n"
        f"Dietary notes: {payload.dietary_notes or 'none'}\n"
        f"Restrictions: {_flag_text(restrictions)}\n"
        f"Sweetness: {payload.sweetness}\n"
        f"Texture: {payload.texture or 'balanced'}\n"
        f"Skill level: {payload.skill_level}\n"
        "Return exact ingredients, prep/bake/rest timing, visual cues, storage, equipment, and why steps matter."
    )
    recipe = _call_openai(prompt)
    if recipe:
        return _finalize(recipe, restrictions)

    return _fallback_recipe(
        "Fudgy Cocoa Sheet Cake",
        f"A custom, detailed bake for '{payload.prompt}', adapted for {_flag_text(restrictions)}.",
        restrictions,
    )


def improve_recipe(payload: ImproveRecipeRequest) -> GeneratedRecipe:
    detected = detect_restrictions(payload.recipe_text, payload.goal)
    restrictions = merge_restrictions(payload.dietary_restrictions, detected)
    prompt = (
        "Improve this baking recipe with professional reasoning.\n"
        f"Goal: {payload.goal}\n"
        f"Restrictions: {_flag_text(restrictions)}\n"
        f"Original recipe:\n{payload.recipe_text}\n"
        "Rewrite ingredients and instructions. Explain every meaningful change in change_notes."
    )
    recipe = _call_openai(prompt)
    if recipe:
        return _finalize(recipe, restrictions)

    return _fallback_recipe(
        "Improved Chocolate Snack Cake",
        f"A rewritten recipe focused on: {payload.goal}.",
        restrictions,
        change_notes=[
            f"Adjusted recipe toward this goal: {payload.goal}.",
            "Balanced sweetness with salt and cocoa so flavor stays strong.",
            "Expanded directions with timing and visual cues to reduce beginner mistakes.",
        ],
    )


def troubleshoot_bake(payload: TroubleshooterRequest) -> TroubleshooterResponse:
    text = f"{payload.description} {payload.recipe_context or ''}".lower()
    issues: list[TroubleshootingIssue] = []
    if "dense" in text or "heavy" in text:
        issues.append(
            TroubleshootingIssue(
                issue="Dense crumb",
                likely_cause="Overmixing, under-leavening, or slicing before the bake cooled.",
                fix_next_time="Mix only until combined, check leavener freshness, and cool fully before cutting.",
                severity="medium",
            )
        )
    if "dry" in text or "crumbly" in text:
        issues.append(
            TroubleshootingIssue(
                issue="Dry texture",
                likely_cause="Too much flour, overbaking, or too little fat/liquid.",
                fix_next_time="Measure flour by weight if possible and start doneness checks 5 minutes earlier.",
                severity="medium",
            )
        )
    if "burn" in text or "dark" in text:
        issues.append(
            TroubleshootingIssue(
                issue="Over-browned edges",
                likely_cause="Oven hot spot, dark pan, or rack too low.",
                fix_next_time="Use the center rack, rotate once, and reduce oven temperature by 15 F if needed.",
                severity="low",
            )
        )
    if not issues:
        issues.append(
            TroubleshootingIssue(
                issue="Needs more context",
                likely_cause="The description does not point to one clear baking fault.",
                fix_next_time="Add details about texture, color, pan size, oven temperature, and bake time.",
                severity="low",
            )
        )
    return TroubleshooterResponse(
        summary="BakeLab analyzed the described result and mapped it to likely baking causes.",
        likely_issues=issues,
        next_bake_plan=[
            "Record actual oven temperature with an oven thermometer.",
            "Start checking doneness at the earliest recommended time.",
            "Write down pan material, rack position, and cooling time for comparison.",
        ],
        confidence=0.78 if len(issues) > 1 else 0.62,
    )
