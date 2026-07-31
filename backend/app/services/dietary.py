from __future__ import annotations

from app.schemas.ai import DietaryRestriction, GeneratedRecipe, RecipeValidation


RESTRICTION_KEYWORDS: dict[DietaryRestriction, tuple[str, ...]] = {
    "vegan": ("vegan", "plant-based", "plant based"),
    "vegetarian": ("vegetarian",),
    "gluten-free": ("gluten-free", "gluten free", "gf"),
    "dairy-free": ("dairy-free", "dairy free", "no dairy"),
    "egg-free": ("egg-free", "egg free", "no egg", "no eggs"),
    "nut-free": ("nut-free", "nut free", "no nuts", "peanut-free", "peanut free"),
    "reduced-sugar": ("less sweet", "not too sweet", "reduced sugar", "low sugar"),
}

CONFLICT_TERMS: dict[DietaryRestriction, tuple[str, ...]] = {
    "vegan": ("egg", "butter", "milk", "cream", "yogurt", "honey", "gelatin"),
    "dairy-free": ("butter", "milk", "cream", "yogurt", "cheese"),
    "egg-free": ("egg", "meringue"),
    "gluten-free": ("all-purpose flour", "bread flour", "cake flour", "wheat"),
    "nut-free": ("almond", "walnut", "pecan", "hazelnut", "peanut", "cashew"),
    "vegetarian": ("gelatin",),
    "reduced-sugar": (),
}

ALLOWED_PHRASES: tuple[str, ...] = (
    "vegan butter",
    "plant milk",
    "oat milk",
    "soy milk",
    "almond milk",
    "coconut milk",
    "dairy-free milk",
    "dairy free milk",
    "flax binder",
)


def detect_restrictions(*texts: str | None) -> list[DietaryRestriction]:
    joined = " ".join(text or "" for text in texts).lower()
    detected: list[DietaryRestriction] = []
    for restriction, keywords in RESTRICTION_KEYWORDS.items():
        if any(keyword in joined for keyword in keywords):
            detected.append(restriction)
    if "vegan" in detected:
        for implied in ("vegetarian", "dairy-free", "egg-free"):
            if implied not in detected:
                detected.append(implied)  # type: ignore[arg-type]
    return detected


def merge_restrictions(*groups: list[DietaryRestriction]) -> list[DietaryRestriction]:
    merged: list[DietaryRestriction] = []
    for group in groups:
        for restriction in group:
            if restriction not in merged:
                merged.append(restriction)
    if "vegan" in merged:
        for implied in ("vegetarian", "dairy-free", "egg-free"):
            if implied not in merged:
                merged.append(implied)  # type: ignore[arg-type]
    return merged


def validate_recipe(recipe: GeneratedRecipe, restrictions: list[DietaryRestriction]) -> GeneratedRecipe:
    ingredient_text = " ".join(recipe.ingredients).lower()
    detailed_text = " ".join(
        f"{ingredient.amount} {ingredient.notes or ''}" for ingredient in recipe.detailed_ingredients
    ).lower()
    combined = f"{ingredient_text} {detailed_text}"
    normalized = combined
    for phrase in ALLOWED_PHRASES:
        normalized = normalized.replace(phrase, "")

    warnings: list[str] = []
    honored: list[DietaryRestriction] = []
    for restriction in restrictions:
        conflicts = [term for term in CONFLICT_TERMS[restriction] if term in normalized]
        if conflicts:
            warnings.append(
                f"Potential {restriction} conflict: found {', '.join(sorted(set(conflicts)))}. Review ingredients before baking."
            )
        else:
            honored.append(restriction)

    confidence = 0.92 if not warnings else 0.62
    recipe.validation = RecipeValidation(
        detected_restrictions=restrictions,
        honored_restrictions=honored,
        warnings=warnings,
        confidence=confidence,
    )
    return recipe
