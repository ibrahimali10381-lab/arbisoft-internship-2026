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

- **Prompt:** “Update the Phase 3 proposal to match the mentor gate slide (problem, users, AI features, stack, data sources, ~3.5-week milestones, risks).”
- **Outcome:** First draft was a NotesLab upgrade (research desk + Chroma). Mentor-facing rewrite still pending originality.

- **Prompt:** “The proposal should be about something new that hasn’t been done but still in scope.”
- **Why:** NotesLab already covers notes CRUD, SerpAPI research, supervisor/workers, MCP, and tracing — Phase 3 cannot just polish that.
- **Outcome:** First rewrite was **BlockerRelay** (incident playbooks). User asked to change it.

- **Prompt:** “change”
- **Outcome:** Replaced the proposal with **DraftHours** (mentor-gated Q&A queue). User asked to change it again.

- **Prompt:** “change” → picked **StudySprint** from five options.
- **Correction applied:** After two rejected ideas, stopped guessing and asked the user to choose a domain.
- **Outcome:** Proposal is now **StudySprint**: upload course PDFs → agents extract topics and generate page-cited questions → grader scores free-text answers against the source → scheduler prioritizes weak topics until the exam date.

## Phase 3 — StudySprint build (Week 5b scaffold, Week 6 core, Week 7 polish)

- **Prompt:** "Complete the app" (with the Week 5b / 6 / 7 syllabus screenshot).
- **Pattern used:** Proposal → scaffold → vertical slices, each tested before moving on.
  - Slice order: auth → ingest → topics → questions → grading → scheduler → agent → RAG → compare → Docker.
- **Scaffold prompts:**
  - "Scaffold a FastAPI + SQLAlchemy backend for StudySprint with User, Course, Document, Chunk, Topic, Question and Attempt models, JWT auth, and an `app/ai` package containing a tool registry, an agent runner and a model client."
  - "Write a model router that tries providers in priority order, validates JSON output with Pydantic, retries once with the validation error, falls back to the next model, and caches results."
  - "Add an OpenAI-compatible provider usable for OpenAI, Groq and Ollama, plus an offline local provider so the app and tests run with no API keys."
- **Core feature prompts:**
  - "Extract text per page with pypdf, chunk it, and extract topics. Every topic and question must cite a real page."
  - "Grade a free-text answer against reference_answer and key_points. Return score 0–5, feedback and missing_points. Update topic mastery with 60/40 blending."
  - "Build a scheduler that ranks never-practiced, then weak, then stale topics, and plans each day until the exam, with a final review day."
  - "Add a supervisor that routes a student goal (prepare / quiz / plan / ask) to curriculum, quiz, session, planner and tutor workers, all through the traced tool registry."
- **Week 7 prompts:**
  - "Add a RAG ask endpoint with page citations."
  - "Add /ai/compare to run the same request across 2+ models with latency."
  - "Add guards for invented page numbers and inconsistent grades."
  - "Export the OpenAPI spec, add a single-container Dockerfile and docker-compose, and write a README with an architecture diagram."
- **Test prompts:**
  - "Write unit tests for the scheduler, router (retry, fallback, guard, cache, compare) and providers with mocked HTTP."
  - "Write end-to-end HTTP tests of upload → questions → session → grade → mastery → plan → ask, and every agent intent. Target ≥70% coverage."
- **Corrections applied:**
  - Question generation pulled passages from other pages, so a Deadlocks question cited page 3. The e2e test caught it; generation now prefers the topic's own page.
  - The stemmer split "process"/"processes" into two different key points. Fixed by not stripping "s" from words ending in "ss".
  - Generated questions read "What is thread?" because the regex dropped the article. Fixed by keeping it ("What is a thread?").
  - Frontend tests failed on Node 26: its own `localStorage` global shadows jsdom's and is undefined without a storage file. Fixed with an in-memory Storage shim in the test setup.
- **Outcome:**
  - `studysprint/` app: 40 backend tests at 96% coverage, 8 frontend tests, lint clean.
  - Verified in the browser: login → course → graded session → model comparison.

## Week 8 — Finalization, documentation & presentation

- **Prompt:** Week 8 syllabus screenshot (code freeze, README, prompts.md, presentation, demo video, reflection).
- **Pattern used:** Freeze features → stability fixes only → docs → split history into meaningful commits.
- **Prompts:**
  - "Fix stability issues only. No new features."
    - Outcome: the course delete action now shows an error instead of failing silently.
  - "Add a Render blueprint so the Docker image deploys from GitHub with one click."
  - "Write a 5-minute demo video script with timestamps covering the AI features."
  - "Expand the slide outline into a 20-minute talk: problem → solution → demo → learnings."
  - "Write a reflection: what AI did well, where it failed (with real examples from this repo), lessons learned."
- **Correction applied:** The AI's first README draft implied the Docker image had been verified. I changed it to say Docker was not available locally, and kept every verification claim to things that actually ran.
- **Outcome:** `render.yaml`, `docs/DEMO_VIDEO.md`, `docs/SLIDES.md` (20 min), `docs/REFLECTION.md`, README AI-feature table and deploy guide.
