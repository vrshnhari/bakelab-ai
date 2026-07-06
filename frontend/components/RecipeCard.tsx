import { Clock, Gauge, ListChecks, Save } from "lucide-react";
import type { ReactNode } from "react";
import type { GeneratedRecipe } from "@/types/recipe";

type RecipeCardProps = {
  recipe: GeneratedRecipe | null;
  onSave: () => void;
  saving: boolean;
};

export function RecipeCard({ recipe, onSave, saving }: RecipeCardProps) {
  if (!recipe) {
    return (
      <section className="flex min-h-[34rem] items-center justify-center rounded-lg border border-dashed border-cocoa/25 bg-white/55 p-8 text-center">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-berry">Ready when you are</p>
          <h2 className="mt-3 text-3xl font-bold text-cocoa">Your recipe will appear here</h2>
          <p className="mt-3 max-w-md text-sm leading-6 text-steel/75">
            Try pantry matching, generate a custom bake, or improve a recipe you already love.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-cocoa/10 bg-white p-6 shadow-soft">
      <div className="flex flex-col gap-4 border-b border-cocoa/10 pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-berry">BakeLab result</p>
          <h2 className="mt-2 text-3xl font-bold text-cocoa">{recipe.title}</h2>
          <p className="mt-3 max-w-2xl leading-7 text-steel/80">{recipe.summary}</p>
        </div>
        <button
          type="button"
          onClick={onSave}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-cocoa px-4 text-sm font-semibold text-white transition hover:bg-cocoa/90 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={saving}
          title="Save recipe"
        >
          <Save size={17} />
          {saving ? "Saving" : "Save"}
        </button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <Meta icon={<Clock size={18} />} label="Time" value={recipe.baking_time} />
        <Meta icon={<Gauge size={18} />} label="Difficulty" value={recipe.difficulty} />
        <Meta icon={<ListChecks size={18} />} label="Steps" value={`${recipe.instructions.length} steps`} />
      </div>

      {recipe.missing_items.length > 0 ? (
        <div className="mt-6 rounded-md border border-berry/20 bg-berry/5 p-4">
          <h3 className="font-semibold text-berry">Missing items</h3>
          <p className="mt-2 text-sm text-steel/80">{recipe.missing_items.join(", ")}</p>
        </div>
      ) : null}

      <div className="mt-7 grid gap-7 lg:grid-cols-[0.85fr_1.15fr]">
        <div>
          <h3 className="text-lg font-bold text-cocoa">Ingredients</h3>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-steel/85">
            {recipe.ingredients.map((ingredient) => (
              <li key={ingredient} className="rounded-md bg-dough px-3 py-2">
                {ingredient}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-lg font-bold text-cocoa">Instructions</h3>
          <ol className="mt-3 space-y-3">
            {recipe.instructions.map((step, index) => (
              <li key={`${step.title}-${index}`} className="rounded-md border border-cocoa/10 p-4">
                <p className="text-sm font-bold text-cocoa">
                  {index + 1}. {step.title}
                </p>
                <p className="mt-1 text-sm leading-6 text-steel/80">{step.detail}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {recipe.change_notes.length > 0 ? (
        <NoteList title="Why these changes work" items={recipe.change_notes} />
      ) : null}
      {recipe.tips.length > 0 ? <NoteList title="Baker's notes" items={recipe.tips} /> : null}
    </section>
  );
}

function Meta({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="flex min-h-20 items-center gap-3 rounded-md bg-dough px-4">
      <span className="text-berry">{icon}</span>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-steel/55">{label}</p>
        <p className="mt-1 text-sm font-bold text-cocoa">{value}</p>
      </div>
    </div>
  );
}

function NoteList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mt-7 rounded-md bg-pistachio/10 p-4">
      <h3 className="font-bold text-pistachio">{title}</h3>
      <ul className="mt-2 space-y-1 text-sm leading-6 text-steel/80">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
