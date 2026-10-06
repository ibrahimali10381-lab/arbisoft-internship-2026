# StudySprint — async mentor check-in

**Intern:** Ibrahim Ali · **Date:** 2026-10-05 · **Covers:** Week 5 (second half) scaffold, Week 6 core features, Week 7 polish

## Done

- **Scaffold (Week 5b)**
  - `studysprint/` has a FastAPI backend and a React frontend.
  - The agent runner (supervisor + 5 workers), tool registry (8 tools) and model client router are in place.
  - The README has an architecture diagram, tech choices and the model selection rationale.
- **Core features (Week 6)**
  - JWT auth and owner-only course CRUD.
  - PDF/TXT/MD upload → page extraction → chunking → topic extraction.
  - Page-cited question generation; free-text grading with missing points.
  - A mastery memory per topic, a "weakest topics first" session, and a day-by-day plan to the exam.
  - The "Study agent" panel completes real tasks from a natural-language goal.
- **Polish (Week 7)**
  - RAG "Ask your material" with page citations.
  - Multi-model routing across OpenAI, Groq, Ollama and 2 offline models, plus a side-by-side comparison page.
  - Output safeguards: Pydantic schemas, page and grade guards, one retry with error feedback, fallback chain, and an LRU cache.
  - A trace viewer.
  - OpenAPI spec exported, and a one-container Docker image with docker-compose.
- **Tests**
  - Backend: 40 tests, 96% coverage, including end-to-end HTTP tests of the full study loop.
  - Frontend: 8 tests. Lint is clean on both sides.

## Decisions to flag

1. **TF-IDF instead of ChromaDB.** The proposal listed Chroma. A course is a few hundred chunks, so in-process TF-IDF is instant, needs no embedding API and keeps deployment to one container. The `retrieve()` interface can switch later.
2. **Offline local models.** Two deterministic graders mean the demo and CI need no API keys, and the router always has a fallback that never fails. With a key set, the LLM runs first automatically.

## Risks / next

- **Grading quality.** With no LLM key, the keyword grader is strict about exact terms. Next step: run the comparison page on 20 real answers with `gpt-4o-mini` vs Groq and record agreement.
- **Docker.** Docker isn't installed on my laptop, so the image hasn't been built yet. Next step: verify `docker compose up --build` on a machine with Docker.
- **Scanned PDFs.** These have no text layer and are rejected with a clear message. OCR is out of scope.

## Ask

A 30-minute live demo slot for feedback on grading strictness and the plan UI.
