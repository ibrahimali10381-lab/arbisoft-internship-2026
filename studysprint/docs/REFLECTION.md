# Reflection: building with AI pair-programming

**Intern:** Ibrahim Ali · **Program:** Arbisoft AI-Focused Internship 2026 · **Scope:** Phase 1 (NotesLab, Weeks 1–5) and Phase 3 (StudySprint, Weeks 5b–8)

Every line in this repo was written with an AI coding agent (Cursor). The full prompt log is in [`prompts.md`](../../prompts.md). This document covers what that was actually like.

## What AI did well

- **Scaffolding and boilerplate.**
  - It produced the FastAPI app, SQLAlchemy models, Pydantic schemas, routers, React pages and tooling configs in minutes, all matching the conventions I'd already set in NotesLab.
  - Where it saved the most time: ESLint + Prettier + Vitest, ruff + pytest, and the Dockerfile.
- **Turning a syllabus into a plan.**
  - Given a screenshot of weekly goals, it broke the work into small, verifiable slices.
  - For StudySprint the order was auth → ingest → topics → questions → grading → scheduler → agent → RAG → compare → Docker.
  - Each slice was tested before the next one started.
- **Tests as a safety net.**
  - It wrote unit, integration and end-to-end tests alongside the code: 40 backend tests at 96% coverage.
  - The end-to-end test caught a real grounding bug before I would have noticed it in the UI (see "Where it failed" below).
- **Designing AI safety rails.**
  - Suggesting a model router with schema validation, retry-with-feedback, a fallback chain and caching was the single most valuable design idea.
  - It made the product work with no API keys and stopped bad LLM output from ever reaching the database.
- **Explaining concepts.** The Week 4 agent concepts (planner/executor, memory, tools, MCP) were explained against my own code, which stuck better than reading docs.

## Where AI failed (and how I caught it)

| Failure | How it showed up | Fix |
|---|---|---|
| Ungrounded questions | A "Deadlocks" question cited page 3 (virtual memory) | The end-to-end test asserted source pages; generation now prefers the topic's own page |
| Naive NLP | The stemmer turned "process" into "proces", so "process" and "processes" became two key points | Added a unit test and a `-ss` rule |
| Awkward language | "What is thread?" and "What is Starvation?" | Kept the article and lower-cased sentence-initial terms; I only saw it by using the app in the browser |
| Serialization assumptions | NotesLab tracing deep-copied a SQLAlchemy Session, causing a `TypeError` | Sanitized trace arguments and serialized manually |
| Hidden live API calls in tests | `load_dotenv()` re-populated the SerpAPI key during tests and hit the network | Removed the reload and made tests delete the key explicitly |
| Environment drift | Frontend tests broke on Node 26 because its `localStorage` global shadows jsdom's | Added an in-memory Storage shim in the test setup |
| Proposal originality | The first Phase 3 proposals were NotesLab upgrades, then ideas I didn't want | Stopped letting it guess and asked it to give me options to choose from |
| Over-claiming | It wanted to say "Docker verified" before Docker had ever run on my machine | I made it state plainly what was and wasn't verified (see the README) |

The common thread: **AI code that "looks right" is often subtly wrong at the edges** (grounding, language, environment), and only tests or actually using the app reveal it.

## Lessons learned

1. **Write the test before trusting the feature.** Each AI bug I caught early was caught by an assertion, not by reading code.
2. **Use the product, not just the tests.** The question-wording bugs passed every test and were obvious in 10 seconds in the browser.
3. **Give the AI constraints, not just goals.** "Every question must cite a real page" produced better code than "generate questions".
4. **Keep a deterministic fallback.** Offline local models made CI, demos and development independent of API keys, rate limits and cost.
5. **Small slices and frequent green checks.** Lint + tests + build after every slice kept the AI's mistakes small and local.
6. **Own the decisions.** The AI proposed ChromaDB, cloud-only LLMs and many features. Cutting them (TF-IDF, a local fallback, one container) was my call, and the scope stayed achievable because of it.
7. **Log prompts as you go.** Reconstructing `prompts.md` afterwards is much harder than appending to it after each session.

## What I'd do differently

- Set up the end-to-end test skeleton on day 1 of Phase 3 instead of after the core features.
- Put a real LLM key in CI (with a budget cap) to track how much the LLM and local graders agree, instead of relying only on the offline graders.
- Commit after every slice rather than in larger batches.
