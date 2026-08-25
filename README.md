# Arbisoft Internship 2026 — NotesLab

Full-stack notes app covering **Week 1 (Frontend Fundamentals)** and **Week 2 (Backend, REST, CRUD & ORM)** from the AI-Focused Internship Program.

## Stack

- **Frontend:** React + Vite + TypeScript, React Router, ESLint, Prettier, Vitest
- **Backend:** FastAPI + SQLAlchemy + Pydantic, ruff, pytest

## Quick start

### Backend

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

A demo user (`demo` / `demo@example.com`) is seeded on API startup.

## Checklist coverage

### Week 1

- [x] Cursor + React/Vite setup
- [x] SPA with 3 routes (`/`, `/notes`, `/notes/new`) and shared layout
- [x] Form with client-side validation
- [x] ESLint + Prettier
- [x] 3+ unit tests (Vitest + Testing Library)
- [x] `prompts.md` log

### Week 2

- [x] CRUD REST API for Notes
- [x] ORM models with User → Notes relationship
- [x] Input validation + correct HTTP status codes
- [x] Backend linter (ruff)
- [x] AI-assisted unit tests (pytest)
- [x] `prompts.md` updated

## Useful commands

```bash
# Frontend
cd frontend && npm run lint && npm run format:check && npm test && npm run build

# Backend
cd backend && source .venv/bin/activate
ruff check .
pytest
```
