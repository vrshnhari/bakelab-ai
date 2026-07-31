import { AlertTriangle, CheckCircle2, Clock, Gauge, ListChecks, Save, Sparkles, Thermometer, Trophy } from "lucide-react";
import type { ReactNode } from "react";
import { BakingMode } from "@/components/BakingMode";
import type { BakingJournal, GeneratedRecipe } from "@/types/recipe";

type RecipeCardProps = {
  recipe: GeneratedRecipe | null;
  journal: BakingJournal;
  onJournalChange: (journal: BakingJournal) => void;
  onSave: () => void;
  saving: boolean;
};

export function RecipeCard({ recipe, journal, onJournalChange, onSave, saving }: RecipeCardProps) {
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

      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        {recipe.oven_temperature_f ? (
          <Meta icon={<Thermometer size={18} />} label="Oven" value={`${recipe.oven_temperature_f} F`} />
        ) : null}
        {recipe.yield_amount ? <Meta icon={<Trophy size={18} />} label="Yield" value={recipe.yield_amount} /> : null}
        {recipe.timing ? (
          <Meta icon={<Clock size={18} />} label="Total" value={`${recipe.timing.total_minutes} min`} />
        ) : null}
      </div>

      {recipe.validation ? (
        <div
          className={`mt-6 rounded-md border p-4 ${
            recipe.validation.warnings.length > 0 ? "border-berry/20 bg-berry/5" : "border-pistachio/20 bg-pistachio/10"
          }`}
        >
          <h3 className={`flex items-center gap-2 font-semibold ${recipe.validation.warnings.length > 0 ? "text-berry" : "text-pistachio"}`}>
            {recipe.validation.warnings.length > 0 ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
            Dietary accuracy check
          </h3>
          <p className="mt-2 text-sm leading-6 text-steel/80">
            Honored: {recipe.validation.honored_restrictions.length > 0 ? recipe.validation.honored_restrictions.join(", ") : "no restriction detected"}.
            Confidence: {Math.round(recipe.validation.confidence * 100)}%.
          </p>
          {recipe.validation.warnings.length > 0 ? (
            <ul className="mt-2 space-y-1 text-sm leading-6 text-steel/80">
              {recipe.validation.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {recipe.quality_score ? (
        <div className="mt-6 rounded-md border border-cocoa/10 bg-dough/70 p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="flex items-center gap-2 font-semibold text-cocoa">
                <Sparkles size={18} className="text-berry" />
                Recipe quality check
              </h3>
              <p className="mt-1 text-sm leading-6 text-steel/75">
                Backend scoring checks whether this recipe is clear, safe, timed, and beginner-friendly.
              </p>
            </div>
            <div className="rounded-md bg-white px-4 py-3 text-center">
              <p className="text-2xl font-black text-berry">{recipe.quality_score.overall}</p>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-steel/55">overall</p>
            </div>
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-4">
            <ScorePill label="Clarity" value={recipe.quality_score.clarity} />
            <ScorePill label="Timing" value={recipe.quality_score.timing_detail} />
            <ScorePill label="Dietary" value={recipe.quality_score.dietary_safety} />
            <ScorePill label="Beginner" value={recipe.quality_score.beginner_friendliness} />
          </div>
          {recipe.quality_score.strengths.length > 0 ? (
            <ul className="mt-4 space-y-1 text-sm leading-6 text-steel/80">
              {recipe.quality_score.strengths.map((strength) => (
                <li key={strength}>{strength}</li>
              ))}
            </ul>
          ) : null}
          {recipe.quality_score.improvement_suggestions.length > 0 ? (
            <div className="mt-3 rounded-md bg-white px-3 py-2 text-sm leading-6 text-steel/75">
              <span className="font-bold text-cocoa">Could improve:</span>{" "}
              {recipe.quality_score.improvement_suggestions.join(" ")}
            </div>
          ) : null}
        </div>
      ) : null}

      {recipe.missing_items.length > 0 ? (
        <div className="mt-6 rounded-md border border-berry/20 bg-berry/5 p-4">
          <h3 className="font-semibold text-berry">Missing items</h3>
          <p className="mt-2 text-sm text-steel/80">{recipe.missing_items.join(", ")}</p>
        </div>
      ) : null}

      <BakingMode recipe={recipe} journal={journal} onJournalChange={onJournalChange} />

      <div className="mt-7 grid gap-7 lg:grid-cols-[0.85fr_1.15fr]">
        <div>
          <h3 className="text-lg font-bold text-cocoa">Ingredients</h3>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-steel/85">
            {(recipe.detailed_ingredients?.length ? recipe.detailed_ingredients : recipe.ingredients).map((ingredient) => {
              const label = typeof ingredient === "string" ? ingredient : `${ingredient.amount} ${ingredient.item.toLowerCase()}`;
              const note = typeof ingredient === "string" ? null : ingredient.notes;
              return (
                <li key={label} className="rounded-md bg-dough px-3 py-2">
                  <span className="font-semibold text-cocoa">{label}</span>
                  {note ? <span className="block text-xs text-steel/65">{note}</span> : null}
                </li>
              );
            })}
          </ul>
          {recipe.equipment?.length > 0 ? <NoteList title="Equipment" items={recipe.equipment} compact /> : null}
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
                {step.visual_cue ? (
                  <p className="mt-2 rounded-md bg-dough px-3 py-2 text-xs leading-5 text-steel/75">
                    <span className="font-bold text-cocoa">Look for:</span> {step.visual_cue}
                  </p>
                ) : null}
                {step.why_it_matters ? (
                  <p className="mt-2 text-xs leading-5 text-steel/65">
                    <span className="font-bold text-cocoa">Why:</span> {step.why_it_matters}
                  </p>
                ) : null}
              </li>
            ))}
          </ol>
        </div>
      </div>

      {recipe.change_notes.length > 0 ? (
        <NoteList title="Why these changes work" items={recipe.change_notes} />
      ) : null}
      {recipe.tips.length > 0 ? <NoteList title="Baker's notes" items={recipe.tips} /> : null}
      {recipe.troubleshooting?.length > 0 ? (
        <NoteList
          title="Troubleshooting"
          items={recipe.troubleshooting.map((issue) => `${issue.issue}: ${issue.fix_next_time}`)}
        />
      ) : null}
      {recipe.storage ? <NoteList title="Storage" items={[recipe.storage]} compact /> : null}
    </section>
  );
}

function ScorePill({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-white px-3 py-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-steel/55">{label}</p>
        <p className="text-sm font-black text-cocoa">{value}</p>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-dough">
        <div className="h-full rounded-full bg-berry" style={{ width: `${value}%` }} />
      </div>
    </div>
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

function NoteList({ title, items, compact = false }: { title: string; items: string[]; compact?: boolean }) {
  return (
    <div className={`${compact ? "mt-4" : "mt-7"} rounded-md bg-pistachio/10 p-4`}>
      <h3 className="font-bold text-pistachio">{title}</h3>
      <ul className="mt-2 space-y-1 text-sm leading-6 text-steel/80">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
