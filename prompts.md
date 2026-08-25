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
