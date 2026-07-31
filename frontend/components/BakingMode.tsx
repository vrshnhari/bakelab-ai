"use client";

import {
  BookOpenCheck,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock,
  Heart,
  NotebookPen,
  PackageCheck,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Timer,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { BakingJournal, GeneratedRecipe, RecipeIngredient } from "@/types/recipe";

type BakingModeProps = {
  recipe: GeneratedRecipe;
  journal: BakingJournal;
  onJournalChange: (journal: BakingJournal) => void;
};

export function BakingMode({ recipe, journal, onJournalChange }: BakingModeProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [timerSeconds, setTimerSeconds] = useState(() => stepMinutes(recipe, 0) * 60);
  const [timerRunning, setTimerRunning] = useState(false);

  const totalSteps = recipe.instructions.length;
  const step = recipe.instructions[activeStep];
  const completedCount = journal.completed_steps.length;
  const ingredientList = recipe.detailed_ingredients?.length ? recipe.detailed_ingredients : recipe.ingredients;
  const checkedIngredientCount = journal.checked_ingredients.length;
  const progress = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;
  const isCompleted = journal.completed_steps.includes(activeStep);
  const activeNote = journal.step_notes[String(activeStep)] ?? "";

  const timerLabel = useMemo(() => formatSeconds(timerSeconds), [timerSeconds]);

  useEffect(() => {
    setActiveStep(0);
    setTimerRunning(false);
  }, [recipe.title]);

  useEffect(() => {
    setTimerSeconds(stepMinutes(recipe, activeStep) * 60);
    setTimerRunning(false);
  }, [activeStep, recipe]);

  useEffect(() => {
    if (!timerRunning || timerSeconds <= 0) return;
    const interval = window.setInterval(() => {
      setTimerSeconds((current) => {
        const next = Math.max(current - 1, 0);
        if (next === 0) setTimerRunning(false);
        return next;
      });
    }, 1000);
    return () => window.clearInterval(interval);
  }, [timerRunning, timerSeconds]);

  function toggleStepDone() {
    const completed_steps = journal.completed_steps.includes(activeStep)
      ? journal.completed_steps.filter((stepIndex) => stepIndex !== activeStep)
      : [...journal.completed_steps, activeStep];
    onJournalChange({ ...journal, completed_steps });
  }

  function toggleIngredient(label: string) {
    const checked_ingredients = journal.checked_ingredients.includes(label)
      ? journal.checked_ingredients.filter((item) => item !== label)
      : [...journal.checked_ingredients, label];
    onJournalChange({ ...journal, checked_ingredients });
  }

  function updateStepNote(note: string) {
    onJournalChange({
      ...journal,
      step_notes: {
        ...journal.step_notes,
        [String(activeStep)]: note,
      },
    });
  }

  function goToStep(nextStep: number) {
    setActiveStep(Math.min(Math.max(nextStep, 0), totalSteps - 1));
  }

  if (!step) {
    return null;
  }

  return (
    <section className="mt-7 rounded-lg border border-berry/15 bg-rosewater p-5">
      <div className="flex flex-col gap-4 border-b border-berry/10 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-berry">Cozy baking journal</p>
          <h3 className="mt-2 text-2xl font-black text-cocoa">Bake this recipe with a gentle coach</h3>
          <p className="mt-2 text-sm leading-6 text-steel/75">
            Gather ingredients, follow one step at a time, keep notes, and learn what to try next bake.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm font-bold text-cocoa">
          <div className="rounded-md bg-white px-4 py-3">{checkedIngredientCount}/{ingredientList.length} gathered</div>
          <div className="rounded-md bg-white px-4 py-3">{completedCount}/{totalSteps} steps</div>
        </div>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-white">
        <div className="h-full rounded-full bg-berry transition-all" style={{ width: `${progress}%` }} />
      </div>

      <div className="mt-5 rounded-md bg-white p-4">
        <div className="flex items-center gap-2 text-berry">
          <PackageCheck size={18} />
          <h4 className="font-black text-cocoa">Gather your ingredients</h4>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {ingredientList.map((ingredient) => {
            const label = ingredientLabel(ingredient);
            const checked = journal.checked_ingredients.includes(label);
            return (
              <button
                key={label}
                type="button"
                onClick={() => toggleIngredient(label)}
                className={`flex min-h-12 items-start gap-3 rounded-md border px-3 py-2 text-left text-sm leading-5 transition ${
                  checked ? "border-pistachio/25 bg-pistachio/10 text-cocoa" : "border-cocoa/10 bg-dough/70 text-steel/80 hover:border-berry/25"
                }`}
                title={checked ? "Mark ingredient not gathered" : "Mark ingredient gathered"}
              >
                <span
                  className={`mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded border ${
                    checked ? "border-pistachio bg-pistachio text-white" : "border-cocoa/20 bg-white text-transparent"
                  }`}
                >
                  <Check size={14} />
                </span>
                <span>
                  <span className="font-bold text-cocoa">{label}</span>
                  {typeof ingredient !== "string" && ingredient.notes ? (
                    <span className="block text-xs text-steel/60">{ingredient.notes}</span>
                  ) : null}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_16rem]">
        <div className="rounded-md bg-white p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-bold text-berry">
                Step {activeStep + 1} of {totalSteps}
              </p>
              <h4 className="mt-1 text-xl font-black text-cocoa">{step.title}</h4>
              <p className="mt-2 flex items-center gap-2 text-sm leading-6 text-steel/70">
                <Heart size={16} className="text-berry" />
                {coachLine(activeStep, totalSteps)}
              </p>
            </div>
            <button
              type="button"
              onClick={toggleStepDone}
              className={`inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-black transition ${
                isCompleted ? "bg-pistachio text-white" : "bg-dough text-cocoa hover:bg-berry/10"
              }`}
              title={isCompleted ? "Mark step unfinished" : "Mark step complete"}
            >
              <Check size={17} />
              {isCompleted ? "Done" : "Check Off"}
            </button>
          </div>

          <p className="mt-4 text-sm leading-7 text-steel/85">{step.detail}</p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {step.visual_cue ? <CoachNote label="Look for" value={step.visual_cue} /> : null}
            {step.why_it_matters ? <CoachNote label="Why it matters" value={step.why_it_matters} /> : null}
          </div>

          <label className="mt-4 block rounded-md bg-dough px-3 py-3">
            <span className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.14em] text-berry">
              <NotebookPen size={15} />
              Step note
            </span>
            <textarea
              value={activeNote}
              onChange={(event) => updateStepNote(event.target.value)}
              placeholder="Example: Batter looked thicker than expected, so I folded slowly."
              className="mt-2 min-h-20 w-full resize-none rounded-md border border-cocoa/10 bg-white px-3 py-2 text-sm leading-6 text-steel/85 outline-none ring-berry/20 transition focus:ring-4"
            />
          </label>

          <div className="mt-5 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => goToStep(activeStep - 1)}
              disabled={activeStep === 0}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-cocoa/15 bg-white px-3 text-sm font-bold text-cocoa transition hover:bg-dough disabled:cursor-not-allowed disabled:opacity-40"
              title="Previous step"
            >
              <ChevronLeft size={17} />
              Previous
            </button>
            <button
              type="button"
              onClick={() => goToStep(activeStep + 1)}
              disabled={activeStep === totalSteps - 1}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-cocoa px-3 text-sm font-bold text-white transition hover:bg-cocoa/90 disabled:cursor-not-allowed disabled:opacity-40"
              title="Next step"
            >
              Next
              <ChevronRight size={17} />
            </button>
          </div>
        </div>

        <div className="rounded-md bg-white p-5">
          <div className="flex items-center gap-2 text-berry">
            <Timer size={19} />
            <h4 className="font-black text-cocoa">Step Timer</h4>
          </div>
          <p className="mt-4 text-4xl font-black text-cocoa">{timerLabel}</p>
          <p className="mt-2 text-sm leading-6 text-steel/70">
            {step.time_minutes ? `${step.time_minutes} minute guide for this step.` : "No timer needed for this step."}
          </p>

          <div className="mt-4 grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setTimerRunning((current) => !current)}
              disabled={timerSeconds === 0 || !step.time_minutes}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-berry px-3 text-sm font-black text-white transition hover:bg-berry/90 disabled:cursor-not-allowed disabled:opacity-40"
              title={timerRunning ? "Pause timer" : "Start timer"}
            >
              {timerRunning ? <Pause size={17} /> : <Play size={17} />}
              {timerRunning ? "Pause" : "Start"}
            </button>
            <button
              type="button"
              onClick={() => {
                setTimerRunning(false);
                setTimerSeconds(stepMinutes(recipe, activeStep) * 60);
              }}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-dough px-3 text-sm font-black text-cocoa transition hover:bg-berry/10"
              title="Reset timer"
            >
              <RotateCcw size={17} />
              Reset
            </button>
          </div>

          <div className="mt-4 rounded-md bg-dough px-3 py-3 text-sm leading-6 text-steel/75">
            <Clock size={16} className="mr-2 inline text-berry" />
            {step.temperature_f ? `Bake at ${step.temperature_f} F for this step.` : "Use this as a prep or resting step."}
          </div>
        </div>
      </div>

      <div className="mt-5 rounded-md bg-white p-5">
        <div className="flex items-center gap-2 text-berry">
          <BookOpenCheck size={18} />
          <h4 className="font-black text-cocoa">After-bake reflection</h4>
        </div>
        <p className="mt-2 text-sm leading-6 text-steel/70">
          This is your little baking memory. Write what worked, what changed, or what you want to try next time.
        </p>
        <textarea
          value={journal.reflection}
          onChange={(event) => onJournalChange({ ...journal, reflection: event.target.value })}
          placeholder="Example: Next time I would bake 2 minutes less and add more vanilla."
          className="mt-3 min-h-24 w-full resize-none rounded-md border border-cocoa/10 bg-dough/60 px-3 py-3 text-sm leading-6 text-steel/85 outline-none ring-berry/20 transition focus:ring-4"
        />
        <div className="mt-3 flex items-center gap-2 rounded-md bg-rosewater px-3 py-2 text-sm leading-6 text-steel/75">
          <Sparkles size={16} className="text-berry" />
          Save the recipe when you want to keep this journal with your collection.
        </div>
      </div>
    </section>
  );
}

function CoachNote({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-dough px-3 py-3">
      <p className="text-xs font-black uppercase tracking-[0.14em] text-berry">{label}</p>
      <p className="mt-1 text-sm leading-6 text-steel/80">{value}</p>
    </div>
  );
}

function stepMinutes(recipe: GeneratedRecipe, stepIndex: number) {
  return recipe.instructions[stepIndex]?.time_minutes ?? 0;
}

function ingredientLabel(ingredient: string | RecipeIngredient) {
  if (typeof ingredient === "string") return ingredient;
  return `${ingredient.amount} ${ingredient.item.toLowerCase()}`;
}

function coachLine(stepIndex: number, totalSteps: number) {
  if (stepIndex === 0) return "Start slow. A calm setup makes the whole bake easier.";
  if (stepIndex === totalSteps - 1) return "Almost there. Let the bake finish gently before judging texture.";
  return "Notice texture, smell, and color here. Those clues teach you more than the clock alone.";
}

function formatSeconds(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}
