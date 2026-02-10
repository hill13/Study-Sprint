# StudySprint

A full-stack habit tracker built for students to build consistent study routines. Features streak tracking with a grace day system — miss a day without losing your streak.

**Live Demo:** [study-sprint-pi.vercel.app](https://study-sprint-pi.vercel.app/)

---

## Tech Stack

**Frontend:** React, TypeScript, Tailwind CSS, Recharts, React Router, Vite

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT Authentication

**Deployment:** Vercel (frontend), Render (backend + database)

---

## Features

- **JWT Authentication** — Register, login, and protected routes with token-based auth
- **Habit CRUD** — Create, read, update, and delete study habits
- **Daily Check-ins** — Mark habits as complete each day with duplicate prevention
- **Streak Tracking** — Automatic streak calculation updated on every check-in
- **Grace Day System** — 2 forgiveness days per month so one missed day doesn't break your streak
- **Status Badges** — Color-coded streak status (Safe, Grace Used, At Risk, Broken)
- **Analytics Dashboard** — Weekly check-in charts, completion rates, and streak comparisons using Recharts
- **Responsive UI** — Clean card-based layout with Tailwind CSS

---

## Project Structure

```
Study-Sprint/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app entry point + CORS config
│       ├── database.py          # PostgreSQL connection + session management
│       ├── config.py            # Environment variables
│       ├── models/              # SQLAlchemy database models
│       │   ├── user.py          # User model
│       │   ├── habit.py         # Habit model with schedule + streak rules
│       │   ├── checkin.py       # Check-in model (daily completions)
│       │   └── streak.py        # Streak model (current, best, grace days)
│       ├── schemas/             # Pydantic request/response schemas
│       │   ├── user.py          # User create/response
│       │   ├── habit.py         # Habit create/update/response
│       │   ├── checkin.py       # Check-in create/response
│       │   └── token.py         # JWT token schema
│       ├── routers/             # API endpoint handlers
│       │   ├── auth.py          # Register + login (OAuth2 + JWT)
│       │   ├── habits.py        # Habit CRUD with streak data loading
│       │   ├── checkins.py      # Check-in CRUD with streak updates
│       │   └── analytics.py     # Aggregated analytics endpoint
│       ├── services/            # Business logic
│       │   └── analytics.py     # Weekly stats, completion rate, streak comparison
│       └── utils/               # Helpers
│           └── dependencies.py  # JWT token verification + get_current_user
│
└── frontend/
    └── src/
        ├── main.tsx             # App entry point
        ├── App.tsx              # Routes + AuthProvider setup
        ├── index.css            # Tailwind CSS import
        ├── services/
        │   └── api.ts           # Centralized API calls to backend
        ├── context/
        │   └── AuthContext.tsx   # Auth state management (token, login, logout)
        ├── pages/
        │   ├── Login.tsx        # Login form
        │   ├── Register.tsx     # Registration form
        │   ├── Dashboard.tsx    # Habit list with streak display + check-ins
        │   └── Analytics.tsx    # Charts (Recharts bar charts)
        └── components/
            ├── HabitForm.tsx     # Create new habit form
            └── ProtectedRoute.tsx # Route guard (redirects if not logged in)
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```
DATABASE_URL=postgresql://username:password@localhost:5432/studysprint
SECRET_KEY=your-secret-key
```

Run the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint             | Description                  | Auth |
|--------|----------------------|------------------------------|------|
| POST   | `/auth/register`     | Create a new account         | No   |
| POST   | `/auth/token`        | Login and get JWT token      | No   |
| GET    | `/habits`            | Get all user habits          | Yes  |
| POST   | `/habits`            | Create a new habit           | Yes  |
| GET    | `/habits/{id}`       | Get a single habit           | Yes  |
| PUT    | `/habits/{id}`       | Update a habit               | Yes  |
| DELETE | `/habits/{id}`       | Delete a habit               | Yes  |
| GET    | `/checkins?habit_id` | Get check-ins for a habit    | Yes  |
| POST   | `/checkins`          | Record a check-in            | Yes  |
| DELETE | `/checkins/{id}`     | Delete a check-in            | Yes  |
| GET    | `/analytics/overview`| Get all analytics data       | Yes  |

---

## How Grace Days Work

Each habit gets **2 grace days per month**. If you miss a day, a grace day is used automatically instead of breaking your streak. Grace days reset on the 1st of each month.

Streak statuses:
- **Safe** — On track, no missed days
- **Grace Used** — Missed a day but saved by a grace day
- **At Risk** — All grace days used, next miss breaks the streak
- **Broken** — Streak has been reset

---

## What I Learned

- Designing a REST API with FastAPI and SQLAlchemy ORM
- JWT authentication flow (register, login, token verification, protected routes)
- React state management with Context API for auth
- Parent-child component communication with props and callbacks
- Solving the N+1 query problem with SQLAlchemy's `joinedload`
- TypeScript strict mode and type safety across the full stack
- Deploying a full-stack app (Vercel + Render + PostgreSQL)
- Building a grace day system that tracks streaks with forgiveness logic
