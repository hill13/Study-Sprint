# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StudySprint is a full-stack habit tracker with streak tracking, grace days, analytics, and AI-powered coaching insights.

- **Frontend**: React + TypeScript + Tailwind + Recharts → deployed on Vercel
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL → deployed on Render
- **Live URLs**: Frontend `https://study-sprint-pi.vercel.app/` | Backend `https://studysprint-api.onrender.com`

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # runs at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

Python version is pinned to 3.10.1 via `backend/.python-version` (Render compatibility).

### Frontend
```bash
cd frontend
npm install
npm run dev      # runs at http://localhost:5173
npm run build    # TypeScript check + Vite bundle
npm run lint
```

## Architecture

### Request Flow
```
React (frontend) → FastAPI (backend) → PostgreSQL (database)
                                     → OpenAI API (AI insights)
```

### Backend Layers
1. **Routers** (`app/routers/`) — HTTP handlers, dependency injection, rate limiting
2. **Services** (`app/services/`) — business logic: streak calculation, analytics aggregation, AI streaming
3. **Models** (`app/models/`) — SQLAlchemy ORM: User, Habit, CheckIn, Streak
4. **Schemas** (`app/schemas/`) — Pydantic request/response contracts
5. **Utils** (`app/utils/`) — JWT auth, password hashing, `get_current_user` dependency

### Frontend Structure
- `src/App.tsx` — route definitions, AuthProvider setup
- `src/services/api.ts` — all HTTP calls go through here (uses `fetchWithAuth` helper)
- `src/context/AuthContext.tsx` — JWT token stored in localStorage, survives refresh
- `src/pages/` — Login, Register, Dashboard, Analytics
- `src/components/` — HabitForm, CheckInCalendar, AIInsights, ProtectedRoute

### Auth Flow
1. Login returns JWT signed with `SECRET_KEY` (HS256)
2. Token stored in `localStorage`, attached as `Authorization: Bearer {token}` on every request
3. Backend `get_current_user()` dependency verifies token and injects user into all protected endpoints
4. All data queries filter by `current_user.id` — users only access their own data

### Key Design Decisions
- **Grace Day System**: Each habit gets 2 forgiveness days/month before streak breaks. Logic lives in `services/streak.py`. Grace days reset on the 1st of each month.
- **Streak table**: Separate `Streak` model stores `current_streak`, `best_streak`, `grace_days_used`, `streak_status` per habit.
- **Single analytics endpoint**: `GET /analytics/overview` bundles all chart data to minimize frontend requests.
- **AI Insights**: `POST /ai/insights` calls OpenAI with streaming (SSE). Rate limited to 1 request/60 seconds per user via in-memory dict. Frontend reads `response.body` as a `ReadableStream` — does NOT use the `api.ts` helper since `response.json()` can't stream. **Local-only** — `AIInsights` component is built (`src/components/AIInsights.tsx`) but not rendered in `Analytics.tsx` on deployment since no free API key is available. To enable locally, add `<AIInsights />` to `Analytics.tsx` and set `OPENAI_API_KEY` in `backend/.env`.
- **Habit response shape**: Habit + Streak data merged into one flat response object (no nested objects on frontend).

## Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=sqlite:///./studysprint.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-key-here
```
Loaded via `pydantic_settings.BaseSettings` in `app/config.py` with `lru_cache` — restart server after changing `.env`.

### Frontend
No `.env` needed locally — defaults to `http://localhost:8000`. Production uses `VITE_API_URL` set in Vercel dashboard.

## TypeScript Notes
- `verbatimModuleSyntax: true` requires `import type` for type-only imports
- Recharts v3 needs manual declaration in `src/declarations.d.ts`
- `npm run build` runs `tsc -b` first — TypeScript errors will fail the Vercel deploy
