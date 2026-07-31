export type RecipeStep = {
  title: string;
  detail: string;
  time_minutes?: number | null;
  temperature_f?: number | null;
  visual_cue?: string | null;
  why_it_matters?: string | null;
};

export type RecipeIngredient = {
  item: string;
  amount: string;
  notes?: string | null;
  optional: boolean;
  substitutions: string[];
};

export type RecipeTiming = {
  prep_minutes: number;
  bake_minutes: number;
  rest_minutes: number;
  total_minutes: number;
};

export type RecipeValidation = {
  detected_restrictions: string[];
  honored_restrictions: string[];
  warnings: string[];
  confidence: number;
};

export type RecipeQualityScore = {
  overall: number;
  clarity: number;
  timing_detail: number;
  dietary_safety: number;
  beginner_friendliness: number;
  strengths: string[];
  improvement_suggestions: string[];
};

export type TroubleshootingIssue = {
  issue: string;
  likely_cause: string;
  fix_next_time: string;
  severity: "low" | "medium" | "high";
};

export type BakingJournal = {
  checked_ingredients: string[];
  completed_steps: number[];
  step_notes: Record<string, string>;
  reflection: string;
};

export type GeneratedRecipe = {
  title: string;
  summary: string;
  ingredients: string[];
  detailed_ingredients: RecipeIngredient[];
  instructions: RecipeStep[];
  baking_time: string;
  timing?: RecipeTiming | null;
  difficulty: string;
  yield_amount: string;
  oven_temperature_f?: number | null;
  equipment: string[];
  storage?: string | null;
  tips: string[];
  missing_items: string[];
  change_notes: string[];
  validation: RecipeValidation;
  quality_score?: RecipeQualityScore | null;
  troubleshooting: TroubleshootingIssue[];
};

export type SavedRecipe = {
  id: string;
  title: string;
  folder: string;
  tags: string[];
  recipe: GeneratedRecipe;
  baking_journal?: BakingJournal | null;
  notes?: string;
  created_at: string;
  updated_at: string;
};
