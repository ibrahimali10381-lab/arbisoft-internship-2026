# Arbisoft Internship 2026 — NotesLab

Full-stack notes app covering Weeks 1–4 of the AI-Focused Internship Program.

## Stack

- **Frontend:** React + Vite + TypeScript, React Router, ESLint, Prettier, Vitest
- **Backend:** FastAPI + SQLAlchemy + JWT auth + SerpAPI research agent, ruff, pytest

## Quick start

### Backend

```bash
cd backend
source .venv/bin/activate
cp .env.example .env   # set SERPAPI_API_KEY for live search
# optional: export $(grep -v '^#' .env | xargs)
uvicorn app.main:app --reload --port 8000
```

Seeded users:

- `demo` / `demopass` (role: user)
- `admin` / `adminpass` (role: admin)

Without `SERPAPI_API_KEY`, the research agent still runs using a demo search fallback.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173 · API docs: http://127.0.0.1:8000/docs

## Checklist coverage

### Weeks 1–2

SPA routes, validated forms, notes CRUD API, ORM relationship, lint + tests, `prompts.md`.

### Week 3

- [x] JWT authentication (`/api/auth/register`, `/login`, `/me`)
- [x] RBAC (admin-only user list; owners/admins manage notes)
- [x] Frontend login + authenticated end-to-end CRUD
- [x] 5+ API tests for auth/CRUD/errors + 1 integration happy-path test
- [x] `prompts.md` updated

### Week 4

- [x] Research agent with SerpAPI web-search skill
- [x] Session memory that recalls earlier facts
- [x] `/research` UI wired to the agent API

## Useful commands

```bash
cd frontend && npm run lint && npm test && npm run build
cd backend && source .venv/bin/activate && ruff check . && pytest
```
