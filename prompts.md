# Prompt Log — Arbisoft Internship 2026

Log of significant prompts used while building NotesLab with Cursor.

## Session setup

- **Prompt:** “Complete all tasks from this Arbisoft Internship Program 2026 syllabus (Week 1 frontend + Week 2 backend).”
- **Why:** Start from the official checklist instead of inventing scope.
- **Outcome:** Proposed defaults (React/Vite + FastAPI Notes app). Confirmed with “defaults are fine,” then created `~/arbisoft-internship-2026`.

## Week 1 — Frontend Fundamentals

- **Prompt:** “Set up a React + Vite + TypeScript app in Cursor. I need at least 3 routes, a shared layout, and ESLint + Prettier configured from day one.”
- **Pattern used:** Context-setting + explicit acceptance criteria.
- **Outcome:** SPA with `/`, `/notes`, `/notes/new`, shared `Layout`, ESLint/Prettier scripts.

- **Prompt:** “Build a note form with client-side validation. Title must be at least 3 characters and content at least 5. Don’t submit if invalid.”
- **Pattern used:** Step-by-step constraints for controlled inputs.
- **Outcome:** `NoteForm` + `validateNoteForm` helper.

- **Prompt:** “Write at least 3 Vitest + React Testing Library unit tests for the note form validation and submit behavior.”
- **Pattern used:** Test-first style request with library named.
- **Outcome:** 5 tests covering validation helpers + invalid/valid submit paths.

- **Prompt:** “Keep a prompts.md and log every significant prompt I use this week.”
- **Pattern used:** Process requirement from the syllabus.
- **Outcome:** This file created and maintained.

## Week 2 — Backend, REST, CRUD & ORM

- **Prompt:** “Create a FastAPI CRUD API for Notes. Use SQLAlchemy, add a User → Notes relationship, and return proper HTTP status codes.”
- **Pattern used:** Decomposition (models → schemas → routers).
- **Outcome:** `/api/notes` CRUD + User model relationship.

- **Prompt:** “Add Pydantic validation for note title/content and reject empty updates with 400. Also configure ruff and make sure lint passes.”
- **Pattern used:** Error-path + tooling request.
- **Outcome:** Schema constraints, 400 on empty update, clean `ruff check`.

- **Prompt:** “Generate pytest tests for create/list/get/update/delete and for validation/404 cases. I’ll review them before committing.”
- **Pattern used:** AI-assisted tests + human review loop.
- **Outcome:** Backend test suite covering happy path and error paths.

## Week 3 — Auth, Authorization, API Tests & Integration

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

## Week 4 leftovers + Week 5 — MCP & multi-agent

- **Prompt:** “Add this” (Week 5 syllabus: MCP server, supervisor/workers, tracing, Phase 3 proposal; plus Week 4 hooks/file plugin/multi-hop).
- **Pattern used:** Syllabus checklist → small verifiable slices (hooks → plugin → supervisor → MCP → proposal).
- **Outcome:**
  - Timestamped tool-call hooks + `TraceStore`
  - `sample_docs/` file-read plugin (txt/pdf)
  - Multi-hop agent demo + `/agents` UI
  - MCP server/client under `backend/mcp_server/`
  - Supervisor routing to research/notes/file workers
  - `docs/PHASE3_PROPOSAL.md` for mentor gate
  - `prompts.md` updated

- **Prompt correction note:** First tracing implementation tried `dataclasses.asdict` on events that still referenced SQLAlchemy sessions → `TypeError`. Fixed by sanitizing hook arguments and manual trace serialization.

- **Prompt:** “diffrent proposal” / “nothing to do with notes”
- **Outcome:** Replaced NotesLab/PulseBrief drafts with **ClaimCheck** — an agentic claim verifier (SerpAPI evidence + supervisor/workers + traces). No notes/journal product.
