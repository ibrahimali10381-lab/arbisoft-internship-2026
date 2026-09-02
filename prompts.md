# Prompt Log — Arbisoft Internship 2026

Log of significant prompts used while building NotesLab.

## Session setup

- **Prompt:** Complete all tasks from the Arbisoft Internship Program 2026 syllabus image (Week 1 frontend + Week 2 backend).
- **Why:** Kick off the project from the curriculum checklist.
- **Outcome:** Agreed on defaults — React/Vite + FastAPI Notes app under `~/arbisoft-internship-2026`.

- **Prompt:** Defaults are fine.
- **Why:** Confirm project name and stack without extra preferences.
- **Outcome:** Created monorepo with `frontend/` and `backend/`, then implemented checklist items.

## Week 1 — Frontend

- **Prompt:** Scaffold a React + Vite + TypeScript SPA with routing, shared layout, validated note form, ESLint/Prettier, and Vitest tests.
- **Pattern used:** Context-setting (internship checklist) + step-by-step decomposition (routes → form → lint → tests).
- **Outcome:** Routes `/`, `/notes`, `/notes/new`; `NoteForm` validation; Vitest coverage for validation helpers and form submit behavior.

## Week 2 — Backend

- **Prompt:** Build a FastAPI CRUD Notes API with SQLAlchemy User→Notes relationship, Pydantic validation, ruff, and pytest.
- **Pattern used:** Step-by-step decomposition (models → schemas → routers → tests → lint).
- **Outcome:** `/api/notes` CRUD, `/api/users` create/list/get, status codes 201/204/400/404/409/422, pytest suite verifying happy path and validation/error cases.

## Review / verification

- **Prompt:** Run frontend lint/tests and backend ruff/pytest; fix any failures so the checklist commits cleanly.
- **Pattern used:** Verify-then-fix loop with AI-assisted test review.
- **Outcome:** Frontend — ESLint/Prettier clean, 5 Vitest tests passing, production build OK. Backend — ruff clean, 5 pytest tests passing. Committed a clean lint/test pass.

## Week 3 — Auth, authorization, API tests & integration

- **Prompt:** Complete Week 3: add JWT auth, one RBAC rule, connect frontend login + authenticated CRUD, write 5+ API tests and 1 integration happy-path test, update prompts.md.
- **Pattern used:** Context from syllabus + step-by-step (security helpers → protected routers → frontend auth → tests).
- **Outcome:** `/api/auth/*`, Bearer-protected notes, admin-only `/api/users`, login UI, pytest coverage for auth/CRUD/RBAC/errors + integration path.

## Week 4 — Agent concepts (SerpAPI)

- **Prompt:** Complete Week 4 using SerpAPI: build a research agent with web-search skill and session memory that recalls earlier facts.
- **Pattern used:** Agent architecture decomposition (planner → SerpAPI executor → memory write/recall) with offline demo fallback when no API key.
- **Outcome:** `SerpApiSearchSkill`, in-process `MemoryStore`, `/api/agent/research` + memory endpoints, `/research` page, agent memory test.
