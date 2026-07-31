# BakeLab AI

An AI-powered baking assistant for home bakers. BakeLab helps users turn pantry ingredients into recipe ideas, generate custom bakes, improve existing recipes, and save favorites.

## MVP Features

- Pantry Assistant: enter ingredients and get recipe ideas with missing items called out.
- AI Recipe Generator: describe a bake and receive ingredients, equipment, steps, timing, doneness cues, storage notes, and difficulty.
- Recipe Improver: paste a recipe and request changes like less sweet, gluten-free, fudgier, vegan, or healthier.
- Saved Recipes: local JSON fallback or PostgreSQL/Supabase persistence with search, folders, tags, baking journal notes, update, and delete routes.
- Baking Troubleshooter: text-based diagnostic endpoint that maps baking issues to likely causes and next-bake fixes.
- Dietary Guardrails: backend validation detects vegan, dairy-free, egg-free, gluten-free, nut-free, and reduced-sugar requests.
- Rate-Limited AI Routes: protects recipe generation endpoints from spam and runaway API costs.
- Recipe Quality Scoring: deterministic backend checks for clarity, timing detail, dietary safety, and beginner friendliness.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python
- Database: JSON-backed local fallback plus PostgreSQL/Supabase support through SQLAlchemy
- Auth: Clerk-ready frontend placeholder
- AI: OpenAI API-ready backend service
- Deployment: Vercel frontend, Render backend

## Project Structure

```txt
backend/           FastAPI app, AI services, validation, tests, and recipe storage
frontend/          Next.js app, components, and API client
frontend-preview/  Static polished demo used for simple Vercel deployment
```

## Backend API

The backend is the portfolio-grade part of the app. It exposes typed REST endpoints:

```txt
POST   /api/ai/pantry
POST   /api/ai/generate
POST   /api/ai/improve
POST   /api/ai/troubleshoot
GET    /api/recipes
GET    /api/recipes/{recipe_id}
POST   /api/recipes
PATCH  /api/recipes/{recipe_id}
DELETE /api/recipes/{recipe_id}
```

Recipe responses include both simple frontend-compatible fields and richer fields:

- `ingredients` and `instructions` for basic rendering.
- `detailed_ingredients` with substitutions and notes.
- `timing` with prep, bake, rest, and total minutes.
- `equipment`, `storage`, `yield_amount`, and `oven_temperature_f`.
- `validation` showing detected/honored dietary restrictions and warnings.
- `quality_score` with overall, clarity, timing, dietary safety, and beginner-friendliness scores.
- `troubleshooting` suggestions for common baking failure modes.

Saved recipe records can also include a `baking_journal` with gathered ingredients, completed steps, per-step notes, and an after-bake reflection.

AI endpoints are rate-limited by client IP. The default is 10 AI requests per hour and can be changed with:

```bash
AI_RATE_LIMIT_REQUESTS=10
AI_RATE_LIMIT_WINDOW_SECONDS=3600
```

## Local Setup

### Backend

```bash
cd backend
python3 -m venv .venv-clean
source .venv-clean/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONDONTWRITEBYTECODE=1 python run.py
```

The backend works without an OpenAI key by returning detailed fallback recipes. Add `OPENAI_API_KEY` to use OpenAI-backed generation.

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Saved recipes use local JSON when `DATABASE_URL` is blank. To use local PostgreSQL instead:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql://bakelab:bakelab@localhost:5432/bakelab
```

To use Supabase, copy the project database connection string from Supabase and set it as `DATABASE_URL`. The backend normalizes standard `postgres://` and `postgresql://` URLs for the installed `psycopg` driver.

Run backend tests:

```bash
cd backend
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Public Static Preview

The polished demo version lives in `frontend-preview/` and can be deployed as a static site.

### Netlify

1. Go to https://app.netlify.com/drop
2. Drag the `frontend-preview` folder into the page.
3. Netlify will give you a public URL immediately.

### GitHub Pages

1. Push this repo to GitHub.
2. In GitHub, open Settings -> Pages.
3. Set the source to GitHub Actions.
4. Push to the `main` branch. The included workflow publishes `frontend-preview/`.

### Vercel

Import the repo and set the output/static directory to `frontend-preview`.

## GitHub Portfolio Notes

This repo is designed to demonstrate more than API calling:

- Clear product flows for real home-baking problems.
- Typed frontend API client and reusable UI components.
- REST backend with request/response schemas.
- OpenAI service abstraction with structured output and fallback generation.
- Dietary validation layer that catches conflicts like vegan recipes containing eggs or dairy.
- In-memory rate limiter for AI routes, designed so it can later move to Redis for multi-server deployments.
- Deterministic recipe quality scoring that evaluates AI output with app-owned rules.
- Repository layer that can save recipes to local JSON or PostgreSQL/Supabase with the same API routes.
- Cozy Baking Journal mode that turns recipe output into a guided bake-along workflow.
- Backend tests for generation, saved recipes, and troubleshooting.
