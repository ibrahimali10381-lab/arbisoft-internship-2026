# Prompt Log — Arbisoft Internship 2026
Log of significant prompts used while building NotesLab.
Log of significant prompts used while building NotesLab with Cursor.
## Session setup
- **Prompt:** Complete all tasks from the Arbisoft Internship Program 2026 syllabus image (Week 1 frontend + Week 2 backend).
- **Why:** Kick off the project from the curriculum checklist.
- **Outcome:** Agreed on defaults — React/Vite + FastAPI Notes app under `~/arbisoft-internship-2026`.
- **Prompt:** “Complete all tasks from this Arbisoft Internship Program 2026 syllabus (Week 1 frontend + Week 2 backend).”
- **Why:** Start from the official checklist instead of inventing scope.
- **Outcome:** Proposed defaults (React/Vite + FastAPI Notes app). Confirmed with “defaults are fine,” then created `~/arbisoft-internship-2026`.
- **Prompt:** Defaults are fine.
- **Why:** Confirm project name and stack without extra preferences.
- **Outcome:** Created monorepo with `frontend/` and `backend/`, then implemented checklist items.
## Week 1 — Frontend Fundamentals
## Week 1 — Frontend
- **Prompt:** “Set up a React + Vite + TypeScript app in Cursor. I need at least 3 routes, a shared layout, and ESLint + Prettier configured from day one.”
- **Pattern used:** Context-setting + explicit acceptance criteria.
- **Outcome:** SPA with `/`, `/notes`, `/notes/new`, shared `Layout`, ESLint/Prettier scripts.
- **Prompt:** Scaffold a React + Vite + TypeScript SPA with routing, shared layout, validated note form, ESLint/Prettier, and Vitest tests.
- **Pattern used:** Context-setting (internship checklist) + step-by-step decomposition (routes → form → lint → tests).
- **Outcome:** Routes `/`, `/notes`, `/notes/new`; `NoteForm` validation; Vitest coverage for validation helpers and form submit behavior.
- **Prompt:** “Build a note form with client-side validation. Title must be at least 3 characters and content at least 5. Don’t submit if invalid.”
- **Pattern used:** Step-by-step constraints for controlled inputs.
- **Outcome:** `NoteForm` + `validateNoteForm` helper.
## Week 2 — Backend
- **Prompt:** “Write at least 3 Vitest + React Testing Library unit tests for the note form validation and submit behavior.”
- **Pattern used:** Test-first style request with library named.
- **Outcome:** 5 tests covering validation helpers + invalid/valid submit paths.
- **Prompt:** Build a FastAPI CRUD Notes API with SQLAlchemy User→Notes relationship, Pydantic validation, ruff, and pytest.
- **Pattern used:** Step-by-step decomposition (models → schemas → routers → tests → lint).
- **Outcome:** `/api/notes` CRUD, `/api/users` create/list/get, status codes 201/204/400/404/409/422, pytest suite verifying happy path and validation/error cases.
- **Prompt:** “Keep a prompts.md and log every significant prompt I use this week.”
- **Pattern used:** Process requirement from the syllabus.
- **Outcome:** This file created and maintained.
## Review / verification
## Week 2 — Backend, REST, CRUD & ORM
- **Prompt:** Run frontend lint/tests and backend ruff/pytest; fix any failures so the checklist commits cleanly.
- **Pattern used:** Verify-then-fix loop with AI-assisted test review.
- **Outcome:** Frontend — ESLint/Prettier clean, 5 Vitest tests passing, production build OK. Backend — ruff clean, 5 pytest tests passing. Committed a clean lint/test pass.
- **Prompt:** “Create a FastAPI CRUD API for Notes. Use SQLAlchemy, add a User → Notes relationship, and return proper HTTP status codes.”
- **Pattern used:** Decomposition (models → schemas → routers).
- **Outcome:** `/api/notes` CRUD + User model relationship.
## Week 3 — Auth, authorization, API tests & integration
- **Prompt:** “Add Pydantic validation for note title/content and reject empty updates with 400. Also configure ruff and make sure lint passes.”
- **Pattern used:** Error-path + tooling request.
- **Outcome:** Schema constraints, 400 on empty update, clean `ruff check`.
- **Prompt:** Complete Week 3: add JWT auth, one RBAC rule, connect frontend login + authenticated CRUD, write 5+ API tests and 1 integration happy-path test, update prompts.md.
- **Pattern used:** Context from syllabus + step-by-step (security helpers → protected routers → frontend auth → tests).
- **Outcome:** `/api/auth/*`, Bearer-protected notes, admin-only `/api/users`, login UI, pytest coverage for auth/CRUD/RBAC/errors + integration path.
- **Prompt:** “Generate pytest tests for create/list/get/update/delete and for validation/404 cases. I’ll review them before committing.”
- **Pattern used:** AI-assisted tests + human review loop.
- **Outcome:** Backend test suite covering happy path and error paths.
## Week 4 — Agent concepts (SerpAPI)
## Week 3 — Auth, Authorization, API Tests & Integration
- **Prompt:** Complete Week 4 using SerpAPI: build a research agent with web-search skill and session memory that recalls earlier facts.
- **Pattern used:** Agent architecture decomposition (planner → SerpAPI executor → memory write/recall) with offline demo fallback when no API key.
- **Outcome:** `SerpApiSearchSkill`, in-process `MemoryStore`, `/api/agent/research` + memory endpoints, `/research` page, agent memory test.
- **Prompt:** “Complete all Week 3 tasks: JWT auth on the Week 2 API, at least one RBAC rule, wire the frontend for login + authenticated CRUD, 5+ API tests, 1 integration happy-path test, update prompts.md.”
- **Pattern used:** Syllabus checklist as single prompt.
- **Outcome:** `/api/auth/register|login|/me`, protected notes, admin-only user list, login UI, expanded pytest suite.
- **Prompt:** “Only admins should list all users. Regular users can only manage their own notes. Admins can delete any note.”
- **Pattern used:** Explicit RBAC rule definition.
- **Outcome:** `require_admin` dependency + owner/admin checks on note mutations.
- **Prompt:** “Add a login/register page and protect /notes routes. Store the JWT and send it on API calls.”
- **Pattern used:** Frontend/backend integration request.
- **Outcome:** `AuthContext`, `ProtectedRoute`, Bearer token in `api/client.ts`.
- **Prompt:** “Write an integration test for the happy path: register → login → create/update/delete note → /me.”
- **Pattern used:** End-to-end API scenario.
- **Outcome:** `test_integration_happy_path_auth_crud`.
## Week 4 — Agent Concepts (SerpAPI)
- **Prompt:** “Complete all tasks, use SerpAPI. Build a research agent with a web-search skill and memory that recalls facts from earlier in the session.”
- **Pattern used:** Tool choice constrained (SerpAPI) + agent primitives.
- **Outcome:** `SerpApiSearchSkill`, session `MemoryStore`, planner → search → memory loop, `/research` page.
- **Prompt:** “Here’s my SerpAPI key — put it in .env so the agent can do live search.”
- **Pattern used:** Secret/config handoff (key kept out of git).
- **Outcome:** `backend/.env` updated; `.env` remains gitignored.
- **Prompt:** “It’s not working.”
- **Pattern used:** Short bug report → diagnose with runtime evidence.
- **Outcome:** Fixed env load timing, surfaced SerpAPI errors in UI; root cause was invalid API key until a valid one was provided.
- **Prompt:** “Explain: What are AI agents? Agents vs chatbots vs copilots, planner → executor → memory, skills, function calling, hooks, memory types, plugins, ReAct, LangChain/LlamaIndex, and Cursor/Windsurf/Claude Code.”
- **Pattern used:** Concept dump from the syllabus topics list.
- **Outcome:** Written explanation tying concepts back to the NotesLab research agent.
## Ops / delivery
- **Prompt:** “Give me steps on how to use it.”
- **Outcome:** Runbook for backend, frontend, login, notes, and research agent.
- **Prompt:** “How can I put this on GitHub?” / “ibrahimali10381-lab”
- **Outcome:** Repo published at https://github.com/ibrahimali10381-lab/arbisoft-internship-2026
- **Prompt:** “Where is the code for the call to SerpAPI?”
- **Outcome:** Pointed to `backend/app/agent/skills.py` (`GoogleSearch(...).get_dict()`).
