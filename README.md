# BakeLab AI

BakeLab AI is a cozy, AI-powered baking assistant for home bakers. It helps users generate detailed recipes, bake from pantry ingredients, improve existing recipes, respect dietary restrictions, and save notes in a baking journal.

## What It Demonstrates

- Full-stack architecture with a Next.js frontend and FastAPI backend.
- AI recipe generation with structured recipe responses.
- Dietary guardrails for vegan, gluten-free, dairy-free, egg-free, nut-free, and reduced-sugar requests.
- Rate limiting for AI endpoints.
- PostgreSQL/Supabase-ready saved recipe storage with local JSON fallback.
- A polished static Vercel preview for quick portfolio demos.

## Core Features

- Pantry Assistant: enter ingredients and get a recipe with missing items highlighted.
- Recipe Generator: describe a bake and receive ingredients, equipment, timing, temperature, doneness cues, and difficulty.
- Recipe Improver: paste a recipe and request changes like vegan, less sweet, fudgier, or healthier.
- Baking Mode: check off ingredients and steps while baking.
- Cozy Baking Journal: save notes about crumb, flavor, mistakes, and next-time changes.
- Recipe Quality Score: evaluates clarity, timing detail, beginner friendliness, and dietary safety.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python
- Database: PostgreSQL/Supabase-ready
- AI: OpenAI API-ready service with local fallback recipes
- Deployment: Vercel for frontend/static preview, Render-ready backend

## Project Structure

```txt
frontend/   Next.js app, UI components, and API client
backend/    FastAPI API, AI service, rate limiter, database models, tests
public/     Static Vercel output used by the current public demo
```

## Local Preview

For the static portfolio preview:

```bash
python3 -m http.server 3000 --bind 127.0.0.1
```

Open `http://127.0.0.1:3000`.

For the full frontend:

```bash
cd frontend
npm install
npm run dev
```

For the backend:

```bash
cd backend
python3 -m venv .venv-clean
source .venv-clean/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

The backend can run without an OpenAI key by returning polished fallback recipes. Add `OPENAI_API_KEY` in `backend/.env` to use the real model.

## Vercel

The root `package.json`, `vercel.json`, `index.html`, and `public/index.html` support the existing static Vercel deployment. The fuller production architecture is:

1. Deploy `backend/` to Render.
2. Add the Render API URL to Vercel as `NEXT_PUBLIC_API_URL`.
3. Deploy `frontend/` from Vercel.

