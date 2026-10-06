# StudySprint — final presentation (20 min + Q&A)

Flow: **problem → solution → demo → how it works → learnings**. Speaker notes follow each slide title.

## 1. Title (0:30)
StudySprint: adaptive quizzes from your own lecture PDFs. Ibrahim Ali, AI-Focused Internship 2026.

## 2. The problem (1:30)
- Rereading is the most common study method and one of the least effective.
- Flashcard apps need hand-written cards. Chatbot "quiz me" sessions forget which topics you keep missing.
- Nothing grades a free-text answer against *your* material and adapts what you practise next.

## 3. Who it's for (0:45)
- University students with lecture PDFs and an exam date.
- Self-learners working through a certification guide.

## 4. The solution (1:15)
Upload, then topics and questions, then answer, then grade, then reschedule weak topics. One loop, grounded in the student's own pages.

## 5. Live demo (6:00)
Follow [`DEMO_VIDEO.md`](DEMO_VIDEO.md):
1. Upload.
2. Graded session (good and bad answers).
3. The plan adapts.
4. Ask with citations.
5. Agent run and trace.
6. Model comparison.

Backup: the recorded video, if the network fails.

## 6. Architecture (1:30)
- Diagram from the README: React → FastAPI → supervisor + 5 workers → tool registry (8 tools) → model router → OpenAI / Groq / Ollama / local.
- SQLite via SQLAlchemy; tracing on every agent, worker, tool and model call.

## 7. The agentic parts (1:30)
- **Supervisor** routes a goal to an intent: prepare / quiz / plan / ask.
- **Workers:** curriculum, quiz, session, planner, tutor.
- **Memory:** per-topic mastery (60/40 blend) plus the course text index used for retrieval.
- **Scheduler:** never practised first, then weak, then stale; ends with a review day.

## 8. Making AI output trustworthy (1:30)
- Pydantic schemas for every task.
- Guards reject invented page numbers and inconsistent grades.
- One retry with the validation error fed back, then fallback to the next model, then the local model, which never fails.
- LRU cache; `/compare` for side-by-side model evaluation.

## 9. Engineering quality (1:00)
- 40 backend tests at 96% coverage, including end-to-end HTTP tests of the full loop; 8 frontend tests.
- ruff, ESLint, Prettier; OpenAPI spec; one Docker image; Render blueprint.

## 10. Phase 1 + 2 concepts used (0:45)
Auth/JWT, CRUD + ORM, file upload, SPA routing, a tool registry, supervisor/workers, memory, structured outputs, tracing, multi-model routing.

## 11. What AI did well / where it failed (2:00)
From [`REFLECTION.md`](REFLECTION.md):
- **Wins:** scaffolding, test generation, and the router design.
- **Failures:**
  - ungrounded questions;
  - naive stemming;
  - awkward question wording;
  - environment drift;
  - over-claiming what had been verified.
- **The point:** tests and actually using the product caught every one.

## 12. Lessons learned (1:00)
- Test before trusting.
- Use the product.
- Give the AI constraints, not just goals.
- Keep a deterministic fallback.
- Own the scope decisions.

## 13. What's next (0:30)
- Embedding retrieval.
- OCR for scanned PDFs.
- A grading agreement study across LLMs.
- Shared courses for study groups.

## 14. Q&A
Likely questions:
- **Why TF-IDF instead of Chroma?** It's small-scale, needs no service, and keeps deployment to one container.
- **How strict is the offline grader?** It looks for exact key terms; LLM grading accepts paraphrases.
- **Cost per session?** Grading 5 answers with `gpt-4o-mini` costs about $0.001, and repeated requests hit the cache.
