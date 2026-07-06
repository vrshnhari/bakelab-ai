import type { GeneratedRecipe, SavedRecipe } from "@/types/recipe";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<TResponse>;
}

async function post<TResponse, TPayload>(path: string, payload: TPayload): Promise<TResponse> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<TResponse>;
}

export function pantryRecipe(ingredients: string[], preferences: string) {
  return post<GeneratedRecipe, { ingredients: string[]; preferences?: string }>("/api/ai/pantry", {
    ingredients,
    preferences,
  });
}

export function generateRecipe(prompt: string, dietaryNotes: string) {
  return post<GeneratedRecipe, { prompt: string; dietary_notes?: string }>("/api/ai/generate", {
    prompt,
    dietary_notes: dietaryNotes,
  });
}

export function improveRecipe(recipeText: string, goal: string) {
  return post<GeneratedRecipe, { recipe_text: string; goal: string }>("/api/ai/improve", {
    recipe_text: recipeText,
    goal,
  });
}

export function saveRecipe(recipe: GeneratedRecipe, folder = "Favorites") {
  return post<SavedRecipe, { title: string; folder: string; recipe: GeneratedRecipe }>("/api/recipes", {
    title: recipe.title,
    folder,
    recipe,
  });
}

export function listSavedRecipes() {
  return get<SavedRecipe[]>("/api/recipes");
}
