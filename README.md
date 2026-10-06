# Arbisoft Internship 2026 — NotesLab

Full-stack notes app covering Weeks 1–5 of the AI-Focused Internship Program.

## Stack

- **Frontend:** React + Vite + TypeScript, React Router, ESLint, Prettier, Vitest
- **Backend:** FastAPI + SQLAlchemy + JWT auth + SerpAPI agents + MCP server, ruff, pytest

## Quick start

### Backend

```bash
cd backend
source .venv/bin/activate
cp .env.example .env   # set SERPAPI_API_KEY for live search
uvicorn app.main:app --reload --port 8000
```

Seeded users:

- `demo` / `demopass` (role: user)
- `admin` / `adminpass` (role: admin)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173 · API docs: http://127.0.0.1:8000/docs

### MCP server + custom client

```bash
cd backend
source .venv/bin/activate
python -m mcp_server.client
```

Cursor connection steps: `backend/mcp_server/README.md`

## Checklist coverage

### Weeks 1–3
SPA, CRUD API, JWT/RBAC, tests, `prompts.md`.

### Week 4
- [x] SerpAPI research agent + session memory
- [x] Hook logging every tool call with timestamps
- [x] File-read plugin (`.txt` / `.pdf` under `sample_docs/`)
- [x] Multi-hop demo (file → memory → web)

### Week 5
- [x] Custom MCP server (`noteslab://app/overview` resource + `search_notes` tool)
- [x] Custom MCP client (+ Cursor config docs)
- [x] Supervisor + ≥2 workers (research / notes / file)
- [x] Tracing layer across the agent graph (`/api/orchestration/traces`, Agents UI)
- [x] Phase 3 project proposal (new product **StudySprint**, not NotesLab): `docs/PHASE3_PROPOSAL.md`

## Phase 3 — StudySprint (Weeks 5b–7)

The Phase 3 product lives in [`studysprint/`](studysprint/README.md). It's a separate app: upload lecture PDFs, and agents write page-cited questions, grade your answers against the source, and schedule weak topics first.

### Week 5 (second half): scaffold
- [x] FastAPI backend + React frontend scaffold, agent runner, tool registry, model client
- [x] README with architecture diagram, tech choices and model selection rationale
- [x] Stubbed entrypoints run end to end on mock data (offline local models + a seeded demo course)
- [x] Async mentor check-in: `studysprint/docs/CHECKIN.md`

### Week 6: core features
- [x] Courses CRUD, PDF/TXT/MD ingest, topic extraction, question generation, grading, mastery, session, plan
- [x] Study agent (supervisor + 5 workers) completes real tasks from a natural-language goal
- [x] Error handling and input validation (upload type/size, schema validation, 404 ownership)
- [x] Tests: 40 backend tests at 96% coverage, 8 frontend tests

### Week 7: advanced AI and polish
- [x] Secondary feature: RAG "Ask your material" with page citations
- [x] Multi-model routing (OpenAI / Groq / Ollama / 2 local) and a `/compare` page
- [x] Output safeguards: Pydantic schemas, guards, retry, fallback, LRU cache
- [x] UX states (loading/error/empty), OpenAPI spec at `studysprint/docs/openapi.json`
- [x] Dockerfile + docker-compose (single container)
- [x] Draft presentation outline: `studysprint/docs/SLIDES.md`

### Week 8: finalization
- [x] Code freeze; stability fixes only
- [x] README: setup, architecture, AI feature docs, deployment (`render.yaml` Render blueprint)
- [x] `prompts.md` covers Phase 1–3
- [x] 20-minute presentation: `studysprint/docs/SLIDES.md`
- [x] Demo video script: `studysprint/docs/DEMO_VIDEO.md` (recording goes to Drive)
- [x] Reflection: `studysprint/docs/REFLECTION.md`

## Useful commands

```bash
cd frontend && npm run lint && npm test && npm run build
cd backend && source .venv/bin/activate && ruff check . && pytest
```
