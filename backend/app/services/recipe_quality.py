from app.schemas.ai import GeneratedRecipe, RecipeQualityScore


def score_recipe(recipe: GeneratedRecipe) -> GeneratedRecipe:
    step_count = max(len(recipe.instructions), 1)
    steps_with_visual_cues = sum(1 for step in recipe.instructions if step.visual_cue)
    steps_with_why = sum(1 for step in recipe.instructions if step.why_it_matters)
    steps_with_time = sum(1 for step in recipe.instructions if step.time_minutes is not None)

    clarity = _score_ratio(
        filled=[
            bool(recipe.summary),
            bool(recipe.detailed_ingredients),
            bool(recipe.equipment),
            steps_with_visual_cues >= step_count * 0.6,
            steps_with_why >= step_count * 0.5,
        ],
    )
    timing_detail = _score_ratio(
        filled=[
            recipe.timing is not None,
            recipe.oven_temperature_f is not None,
            steps_with_time >= step_count * 0.6,
            bool(recipe.baking_time),
        ],
    )
    dietary_safety = int(recipe.validation.confidence * 100)
    if recipe.validation.warnings:
        dietary_safety = min(dietary_safety, 65)

    beginner_friendliness = _score_ratio(
        filled=[
            recipe.difficulty.lower() in {"easy", "beginner", "beginner-friendly"},
            len(recipe.instructions) >= 5,
            bool(recipe.tips),
            bool(recipe.troubleshooting),
            all(len(step.detail) >= 35 for step in recipe.instructions),
        ],
    )

    overall = round((clarity * 0.3) + (timing_detail * 0.25) + (dietary_safety * 0.25) + (beginner_friendliness * 0.2))
    recipe.quality_score = RecipeQualityScore(
        overall=overall,
        clarity=clarity,
        timing_detail=timing_detail,
        dietary_safety=dietary_safety,
        beginner_friendliness=beginner_friendliness,
        strengths=_strengths(recipe, clarity, timing_detail, dietary_safety, beginner_friendliness),
        improvement_suggestions=_suggestions(recipe, clarity, timing_detail, dietary_safety, beginner_friendliness),
    )
    return recipe


def _score_ratio(filled: list[bool]) -> int:
    return round((sum(1 for item in filled if item) / len(filled)) * 100)


def _strengths(
    recipe: GeneratedRecipe,
    clarity: int,
    timing_detail: int,
    dietary_safety: int,
    beginner_friendliness: int,
) -> list[str]:
    strengths: list[str] = []
    if clarity >= 80:
        strengths.append("Clear ingredient structure and step-by-step directions.")
    if timing_detail >= 80:
        strengths.append("Strong timing support with oven temperature and step timing.")
    if dietary_safety >= 90 and recipe.validation.honored_restrictions:
        strengths.append("Dietary restrictions were checked and honored.")
    if beginner_friendliness >= 80:
        strengths.append("Beginner-friendly guidance with tips and troubleshooting.")
    return strengths or ["Recipe has enough structure to start baking with confidence."]


def _suggestions(
    recipe: GeneratedRecipe,
    clarity: int,
    timing_detail: int,
    dietary_safety: int,
    beginner_friendliness: int,
) -> list[str]:
    suggestions: list[str] = []
    if clarity < 80:
        suggestions.append("Add more visual cues and explain why key steps matter.")
    if timing_detail < 80:
        suggestions.append("Add prep, bake, rest, and per-step timing details.")
    if dietary_safety < 90:
        suggestions.append("Review ingredients against the requested dietary restrictions.")
    if beginner_friendliness < 80:
        suggestions.append("Add beginner tips, common mistakes, and troubleshooting notes.")
    return suggestions
