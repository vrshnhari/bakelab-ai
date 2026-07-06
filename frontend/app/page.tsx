"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { BookOpen, ChefHat, ClipboardPen, Search, Sparkles } from "lucide-react";

import { RecipeCard } from "@/components/RecipeCard";
import { generateRecipe, improveRecipe, listSavedRecipes, pantryRecipe, saveRecipe } from "@/lib/api";
import type { GeneratedRecipe, SavedRecipe } from "@/types/recipe";

type Mode = "pantry" | "generate" | "improve";

const modeConfig = {
  pantry: {
    icon: Search,
    label: "Pantry",
    title: "Bake from what you have",
    helper: "Enter ingredients separated by commas and BakeLab will build around them.",
  },
  generate: {
    icon: Sparkles,
    label: "Generate",
    title: "Describe your ideal bake",
    helper: "Ask for a dessert, breakfast bake, dietary style, flavor, texture, or occasion.",
  },
  improve: {
    icon: ClipboardPen,
    label: "Improve",
    title: "Upgrade an existing recipe",
    helper: "Paste a recipe and tell BakeLab what you want to change.",
  },
} satisfies Record<Mode, { icon: typeof Search; label: string; title: string; helper: string }>;

export default function Home() {
  const [mode, setMode] = useState<Mode>("pantry");
  const [ingredients, setIngredients] = useState("flour, butter, eggs, sugar, vanilla");
  const [preferences, setPreferences] = useState("quick, cozy, not too sweet");
  const [prompt, setPrompt] = useState("a chocolate dessert that is fudgy but not too sweet");
  const [dietaryNotes, setDietaryNotes] = useState("");
  const [recipeText, setRecipeText] = useState("");
  const [goal, setGoal] = useState("make it less sweet and more tender");
  const [recipe, setRecipe] = useState<GeneratedRecipe | null>(null);
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[]>([]);
  const [recipeSearch, setRecipeSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");

  const current = modeConfig[mode];
  const Icon = current.icon;

  useEffect(() => {
    listSavedRecipes()
      .then(setSavedRecipes)
      .catch(() => undefined);
  }, []);

  const canSubmit = useMemo(() => {
    if (mode === "pantry") return ingredients.trim().length > 0;
    if (mode === "generate") return prompt.trim().length > 3;
    return recipeText.trim().length > 20 && goal.trim().length > 2;
  }, [goal, ingredients, mode, prompt, recipeText]);

  const filteredRecipes = useMemo(() => {
    const query = recipeSearch.toLowerCase().trim();
    if (!query) return savedRecipes;
    return savedRecipes.filter((item) => {
      const haystack = `${item.title} ${item.folder} ${item.recipe.summary}`.toLowerCase();
      return haystack.includes(query);
    });
  }, [recipeSearch, savedRecipes]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    setStatus("");
    try {
      const result =
        mode === "pantry"
          ? await pantryRecipe(
              ingredients
                .split(",")
                .map((item) => item.trim())
                .filter(Boolean),
              preferences,
            )
          : mode === "generate"
            ? await generateRecipe(prompt, dietaryNotes)
            : await improveRecipe(recipeText, goal);
      setRecipe(result);
    } catch {
      setStatus("Could not reach the BakeLab API. Make sure the FastAPI server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!recipe) return;
    setSaving(true);
    setStatus("");
    try {
      const saved = await saveRecipe(recipe);
      setSavedRecipes((currentRecipes) => [saved, ...currentRecipes]);
      setStatus("Recipe saved to your collection.");
    } catch {
      setStatus("The recipe was generated, but saving failed. Check the backend server.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-cocoa/10 bg-white/75 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-md bg-berry text-white">
              <ChefHat size={22} />
            </span>
            <div>
              <p className="text-xl font-black text-cocoa">BakeLab AI</p>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-steel/55">
                Smart baking assistant
              </p>
            </div>
          </div>
          <a
            href="https://github.com"
            className="hidden rounded-md border border-cocoa/15 px-4 py-2 text-sm font-semibold text-cocoa transition hover:bg-dough sm:inline-flex"
          >
            Portfolio Project
          </a>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 py-8 lg:grid-cols-[25rem_1fr]">
        <aside className="rounded-lg border border-cocoa/10 bg-white p-5 shadow-soft">
          <div className="flex rounded-md bg-dough p-1">
            {(Object.keys(modeConfig) as Mode[]).map((option) => {
              const OptionIcon = modeConfig[option].icon;
              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => setMode(option)}
                  className={`flex h-10 flex-1 items-center justify-center gap-2 rounded px-2 text-sm font-bold transition ${
                    mode === option ? "bg-white text-berry shadow-sm" : "text-steel/65 hover:text-cocoa"
                  }`}
                  title={modeConfig[option].label}
                >
                  <OptionIcon size={16} />
                  <span>{modeConfig[option].label}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-6 flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-berry/10 text-berry">
              <Icon size={19} />
            </span>
            <div>
              <h1 className="text-2xl font-black text-cocoa">{current.title}</h1>
              <p className="mt-2 text-sm leading-6 text-steel/75">{current.helper}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {mode === "pantry" ? (
              <>
                <Field label="Ingredients">
                  <textarea
                    value={ingredients}
                    onChange={(event) => setIngredients(event.target.value)}
                    className="min-h-28 w-full resize-none rounded-md border border-cocoa/15 bg-white px-3 py-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
                <Field label="Preferences">
                  <input
                    value={preferences}
                    onChange={(event) => setPreferences(event.target.value)}
                    className="h-11 w-full rounded-md border border-cocoa/15 bg-white px-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
              </>
            ) : null}

            {mode === "generate" ? (
              <>
                <Field label="What do you want to bake?">
                  <textarea
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    className="min-h-32 w-full resize-none rounded-md border border-cocoa/15 bg-white px-3 py-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
                <Field label="Dietary notes">
                  <input
                    value={dietaryNotes}
                    onChange={(event) => setDietaryNotes(event.target.value)}
                    placeholder="optional"
                    className="h-11 w-full rounded-md border border-cocoa/15 bg-white px-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
              </>
            ) : null}

            {mode === "improve" ? (
              <>
                <Field label="Recipe text">
                  <textarea
                    value={recipeText}
                    onChange={(event) => setRecipeText(event.target.value)}
                    placeholder="Paste ingredients and instructions here"
                    className="min-h-36 w-full resize-none rounded-md border border-cocoa/15 bg-white px-3 py-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
                <Field label="Improvement goal">
                  <input
                    value={goal}
                    onChange={(event) => setGoal(event.target.value)}
                    className="h-11 w-full rounded-md border border-cocoa/15 bg-white px-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
                  />
                </Field>
              </>
            ) : null}

            <button
              type="submit"
              disabled={!canSubmit || loading}
              className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md bg-berry px-4 text-sm font-black text-white transition hover:bg-berry/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Sparkles size={18} />
              {loading ? "Mixing..." : "Create Recipe"}
            </button>
          </form>

          {status ? <p className="mt-4 rounded-md bg-dough px-3 py-2 text-sm text-steel/80">{status}</p> : null}

          <div className="mt-7 border-t border-cocoa/10 pt-5">
            <div className="flex items-center gap-2">
              <BookOpen size={18} className="text-berry" />
              <h2 className="font-black text-cocoa">Saved Recipes</h2>
            </div>
            <input
              value={recipeSearch}
              onChange={(event) => setRecipeSearch(event.target.value)}
              placeholder="Search collection"
              className="mt-3 h-10 w-full rounded-md border border-cocoa/15 bg-white px-3 text-sm outline-none ring-berry/20 transition focus:ring-4"
            />
            <div className="mt-3 max-h-72 space-y-2 overflow-auto pr-1">
              {filteredRecipes.length > 0 ? (
                filteredRecipes.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setRecipe(item.recipe)}
                    className="w-full rounded-md border border-cocoa/10 bg-dough/70 p-3 text-left transition hover:border-berry/30 hover:bg-dough"
                  >
                    <p className="text-sm font-bold text-cocoa">{item.title}</p>
                    <p className="mt-1 line-clamp-2 text-xs leading-5 text-steel/70">{item.recipe.summary}</p>
                  </button>
                ))
              ) : (
                <p className="rounded-md bg-dough/70 p-3 text-sm leading-6 text-steel/70">
                  Saved recipes will show here after you click Save.
                </p>
              )}
            </div>
          </div>
        </aside>

        <RecipeCard recipe={recipe} onSave={handleSave} saving={saving} />
      </section>
    </main>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-cocoa">{label}</span>
      {children}
    </label>
  );
}
