from app.schemas.ai import GeneratedRecipe, RecipeStep, RecipeTiming, RecipeValidation, TroubleshootingIssue
from app.services.recipe_quality import score_recipe


def test_score_recipe_rewards_detailed_beginner_friendly_recipe():
    recipe = GeneratedRecipe(
        title="Detailed Cocoa Cake",
        summary="A careful beginner-friendly cake.",
        ingredients=["1 cup flour", "1/2 cup sugar"],
        detailed_ingredients=[],
        instructions=[
            RecipeStep(
                title="Prep",
                detail="Prepare the pan carefully with parchment and preheat the oven before mixing.",
                time_minutes=8,
                temperature_f=350,
                visual_cue="Pan is lined neatly.",
                why_it_matters="A ready pan keeps batter from sitting too long.",
            ),
            RecipeStep(
                title="Mix",
                detail="Mix the batter gently until the dry ingredients just disappear.",
                time_minutes=4,
                visual_cue="Batter looks glossy.",
                why_it_matters="Gentle mixing keeps the crumb tender.",
            ),
            RecipeStep(
                title="Bake",
                detail="Bake until the center springs back lightly and a tester has moist crumbs.",
                time_minutes=25,
                temperature_f=350,
                visual_cue="Edges are set and center barely wobbles.",
                why_it_matters="Moist crumbs prevent overbaking.",
            ),
            RecipeStep(title="Cool", detail="Cool fully before slicing so the crumb can set.", time_minutes=20),
            RecipeStep(title="Serve", detail="Slice with a clean knife and store leftovers covered.", time_minutes=2),
        ],
        baking_time="25 minutes",
        timing=RecipeTiming(prep_minutes=12, bake_minutes=25, rest_minutes=20, total_minutes=57),
        difficulty="Easy",
        yield_amount="9 squares",
        oven_temperature_f=350,
        equipment=["8-inch pan", "whisk"],
        tips=["Measure flour gently."],
        validation=RecipeValidation(honored_restrictions=["vegan"], confidence=0.94),
        troubleshooting=[
            TroubleshootingIssue(
                issue="Dry edges",
                likely_cause="Overbaking",
                fix_next_time="Check earlier.",
                severity="low",
            )
        ],
    )

    scored = score_recipe(recipe)

    assert scored.quality_score is not None
    assert scored.quality_score.overall >= 80
    assert scored.quality_score.dietary_safety == 94
    assert scored.quality_score.strengths
