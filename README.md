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
- [x] Phase 3 project proposal: `docs/PHASE3_PROPOSAL.md`

## Useful commands

```bash
cd frontend && npm run lint && npm test && npm run build
cd backend && source .venv/bin/activate && ruff check . && pytest
```
