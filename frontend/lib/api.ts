import type { BakingJournal, GeneratedRecipe, SavedRecipe } from "@/types/recipe";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public retryAfterSeconds?: number,
  ) {
    super(message);
  }
}

async function get<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw await apiErrorFromResponse(response);
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
    throw await apiErrorFromResponse(response);
  }

  return response.json() as Promise<TResponse>;
}

async function apiErrorFromResponse(response: Response) {
  let message = `Request failed with status ${response.status}`;
  let retryAfterSeconds: number | undefined;

  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      message = body.detail;
    } else if (body.detail?.message) {
      message = body.detail.message;
      retryAfterSeconds = body.detail.retry_after_seconds;
    }
  } catch {
    // Keep the status-based message when the API does not return JSON.
  }

  return new ApiError(message, response.status, retryAfterSeconds);
}

export function pantryRecipe(ingredients: string[], preferences: string) {
  return post<
    GeneratedRecipe,
    { ingredients: string[]; preferences?: string; dietary_restrictions?: string[] }
  >("/api/ai/pantry", {
    ingredients,
    preferences,
    dietary_restrictions: restrictionsFromText(preferences),
  });
}

export function generateRecipe(prompt: string, dietaryNotes: string) {
  return post<
    GeneratedRecipe,
    { prompt: string; dietary_notes?: string; dietary_restrictions?: string[]; sweetness?: string }
  >("/api/ai/generate", {
    prompt,
    dietary_notes: dietaryNotes,
    dietary_restrictions: restrictionsFromText(`${prompt} ${dietaryNotes}`),
    sweetness: /less sweet|not too sweet|low sugar|reduced sugar/i.test(`${prompt} ${dietaryNotes}`) ? "low" : "medium",
  });
}

export function improveRecipe(recipeText: string, goal: string) {
  return post<GeneratedRecipe, { recipe_text: string; goal: string; dietary_restrictions?: string[] }>("/api/ai/improve", {
    recipe_text: recipeText,
    goal,
    dietary_restrictions: restrictionsFromText(`${recipeText} ${goal}`),
  });
}

export function saveRecipe(recipe: GeneratedRecipe, journal?: BakingJournal, folder = "Favorites") {
  return post<
    SavedRecipe,
    { title: string; folder: string; tags: string[]; recipe: GeneratedRecipe; baking_journal?: BakingJournal }
  >("/api/recipes", {
    title: recipe.title,
    folder,
    tags: recipe.validation?.honored_restrictions ?? [],
    recipe,
    baking_journal: journal,
  });
}

export function listSavedRecipes() {
  return get<SavedRecipe[]>("/api/recipes");
}

function restrictionsFromText(text: string): string[] {
  const lower = text.toLowerCase();
  const restrictions: string[] = [];
  if (lower.includes("vegan")) restrictions.push("vegan");
  if (lower.includes("gluten-free") || lower.includes("gluten free")) restrictions.push("gluten-free");
  if (lower.includes("dairy-free") || lower.includes("dairy free") || lower.includes("no dairy")) restrictions.push("dairy-free");
  if (lower.includes("egg-free") || lower.includes("egg free") || lower.includes("no eggs")) restrictions.push("egg-free");
  if (lower.includes("nut-free") || lower.includes("nut free") || lower.includes("no nuts")) restrictions.push("nut-free");
  if (/less sweet|not too sweet|low sugar|reduced sugar/i.test(text)) restrictions.push("reduced-sugar");
  return [...new Set(restrictions)];
}
