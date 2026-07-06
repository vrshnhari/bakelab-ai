export type RecipeStep = {
  title: string;
  detail: string;
};

export type GeneratedRecipe = {
  title: string;
  summary: string;
  ingredients: string[];
  instructions: RecipeStep[];
  baking_time: string;
  difficulty: string;
  tips: string[];
  missing_items: string[];
  change_notes: string[];
};

export type SavedRecipe = {
  id: string;
  title: string;
  folder: string;
  recipe: GeneratedRecipe;
  notes?: string;
  created_at: string;
  updated_at: string;
};

