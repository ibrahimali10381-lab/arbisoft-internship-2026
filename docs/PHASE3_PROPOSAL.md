# Phase 3 Project Proposal — NotesLab Agentic Workspace

**Intern:** Ibrahim Ali  
**Program:** Arbisoft AI-Focused Internship Program 2026  
**Date:** 2026-09-08  
**Repo:** https://github.com/ibrahimali10381-lab/arbisoft-internship-2026  

## Problem

Interns and small teams capture notes in many places and research topics ad hoc. They need a single workspace that can (1) store authenticated notes, (2) research the web, (3) read local briefing docs, and (4) coordinate those capabilities through agents with observability.

## Proposed solution

Extend NotesLab into an **Agentic Notes Workspace**:

1. **Notes core (done):** JWT auth, RBAC, CRUD API + React SPA  
2. **Single research agent (done):** SerpAPI skill + session memory  
3. **MCP surface (Week 5):** expose NotesLab as an MCP server (`overview` resource + `search_notes` tool) for Cursor / custom clients  
4. **Multi-agent orchestration (Week 5):** supervisor routes to research / notes / file workers with traced tool calls  
5. **Phase 3 build (next):** richer retrieval (vector memory), proposal-approved feature set, mentor demo

## Architecture (target)

```text
User / Cursor MCP client
        │
        ├─ FastAPI API (auth, notes, agent, orchestration)
        ├─ MCP server (stdio): resource + tool
        └─ Supervisor
              ├─ research_worker (SerpAPI)
              ├─ notes_worker (SQL search)
              └─ file_worker (.txt/.pdf plugin)
                    └─ TraceStore (pre/post hooks)
```

## Scope for mentor approval

### In scope
- MCP server + custom client demo  
- Supervisor + ≥2 workers with hand-offs  
- Tool-call tracing UI/API  
- Multi-hop demo (file → memory → web)  
- Documented prompts.md + ground rules  

### Out of scope (for later)
- Production OAuth providers  
- Horizontal scaling / queued workers  
- Full LangChain rewrite  

## Success metrics
- Mentor can connect MCP in Cursor and call `search_notes`  
- Supervisor demo routes a mixed query to ≥2 workers  
- Trace log shows timestamped pre/post events for each tool call  
- All backend tests pass; no secrets committed  

## Risks & mitigations
- **SerpAPI quota/key issues** → demo fallback + clear 502 errors  
- **MCP client variance** → ship custom stdio client + Cursor config snippet  
- **Unsafe file reads** → restrict plugin to `sample_docs/`  

## Ask
Please approve this Phase 3 direction so the remaining half of Week 5 / Phase 3 can deepen retrieval + polish polish on the same NotesLab codebase.
