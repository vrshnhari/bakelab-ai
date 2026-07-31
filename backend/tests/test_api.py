from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_vegan_recipe_honors_restrictions():
    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": "vegan fudgy brownies not too sweet",
            "dietary_notes": "vegan",
            "sweetness": "low",
        },
    )

    assert response.status_code == 200
    recipe = response.json()
    assert recipe["validation"]["warnings"] == []
    assert "vegan" in recipe["validation"]["honored_restrictions"]
    assert "dairy-free" in recipe["validation"]["honored_restrictions"]
    assert "egg-free" in recipe["validation"]["honored_restrictions"]


def test_save_and_search_recipe():
    generated = client.post(
        "/api/ai/generate",
        json={"prompt": "vegan chocolate snack cake", "dietary_notes": "vegan"},
    ).json()

    saved = client.post(
        "/api/recipes",
        json={
            "title": generated["title"],
            "folder": "Tests",
            "tags": ["vegan", "chocolate"],
            "recipe": generated,
        },
    )

    assert saved.status_code == 200
    recipe_id = saved.json()["id"]

    search = client.get("/api/recipes?query=vegan")
    assert search.status_code == 200
    assert any(recipe["id"] == recipe_id for recipe in search.json())


def test_save_recipe_with_baking_journal():
    generated = client.post(
        "/api/ai/generate",
        json={"prompt": "vegan chocolate snack cake", "dietary_notes": "vegan"},
    ).json()
    journal = {
        "checked_ingredients": ["1 cup all-purpose flour"],
        "completed_steps": [0, 1],
        "step_notes": {"0": "Pan was lined before mixing."},
        "reflection": "Next time I would add orange zest.",
    }

    saved = client.post(
        "/api/recipes",
        json={
            "title": generated["title"],
            "folder": "Journal",
            "tags": ["journal"],
            "recipe": generated,
            "baking_journal": journal,
        },
    )

    assert saved.status_code == 200
    assert saved.json()["baking_journal"] == journal


def test_troubleshooter_returns_action_plan():
    response = client.post("/api/ai/troubleshoot", json={"description": "my cake is dense and dry"})

    assert response.status_code == 200
    body = response.json()
    assert body["confidence"] > 0
    assert body["likely_issues"]
    assert body["next_bake_plan"]
