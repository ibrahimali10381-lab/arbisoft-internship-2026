# Phase 3 Project Proposal — StudySprint

**Intern:** Ibrahim Ali  
**Program:** Arbisoft AI-Focused Internship Program 2026  
**Gate:** End of mid-Week 5 — mentor approval required before Phase 3 build  
**Date:** 2026-10-05  
**Related practice repo:** https://github.com/ibrahimali10381-lab/arbisoft-internship-2026  

> This is a **new product**. NotesLab stays the Weeks 1–5 practice app (notes + research agents). StudySprint is built as a separate app.  
> Development will not start until this proposal is approved. Happy to iterate within 48 hours based on mentor feedback.

---

## 1. Problem statement

Students preparing for an exam usually reread slides and PDFs, which feels productive but tells them nothing about what they actually remember. Flashcard apps need cards written by hand, and asking a chatbot to "quiz me" gives one-off questions with no record of which topics the student keeps getting wrong. There is no simple tool that turns a student's own course material into a quiz schedule, grades free-text answers against the source, and keeps shifting practice toward weak topics until the exam date.

## 2. Target users and core use case

**Target users**
- University students preparing for a midterm or final from lecture PDFs  
- Interns or self-learners working through a certification guide  

**Core use case**  
A student uploads 2–5 lecture PDFs and sets an exam date. Agents split the material into topics, generate quiz questions tied to specific pages, and build a day-by-day plan. Each session, the student answers questions in their own words; a grader agent scores each answer against the source text and explains what was missing. Topics with low scores come back sooner; mastered topics fade out. The student sees a per-topic mastery chart counting down to the exam.

Loop: **upload → topics + questions → answer → grade → reschedule weak topics.**

## 3. Key AI feature(s) (agent primitives)

**Primary feature — Adaptive quiz loop**  
The agent decides what to ask next based on the student's past results, grades open answers with citations, and replans the schedule.

| Primitive | How StudySprint uses it |
|---|---|
| **Planner → executor → memory** | Planner picks today's topics from mastery scores → quiz worker asks → grader scores → memory updates mastery |
| **Skills / tools** | `extract_topics`, `generate_questions`, `grade_answer`, `update_mastery`, `plan_sessions` |
| **File plugin** | PDF text extraction per page so every question cites its page |
| **Structured outputs** | Question and grade JSON validated with Pydantic (score 0–5, missing_points[], source_page) |
| **Memory** | Per-topic mastery store + vector index (Chroma) of PDF chunks for grounding |
| **Supervisor + ≥2 workers** | `curriculum_worker` (topics/plan), `quiz_worker` (questions), `grader_worker` (scoring) |
| **Hooks + tracing** | Every grade logs the source chunk used, so a disputed score can be checked |

## 4. Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite + TypeScript (upload, today's session, mastery dashboard) |
| Backend | FastAPI + SQLAlchemy + JWT auth |
| Agents | Custom supervisor/workers (no framework rewrite) |
| LLM | OpenAI-compatible API for question generation and grading; small local fallback model is a stretch goal |
| Retrieval | ChromaDB for PDF chunk embeddings |
| PDF parsing | pypdf |
| Quality | pytest, Vitest, ruff, ESLint, `prompts.md` |

## 5. Data sources / integrations needed

| Source | Purpose |
|---|---|
| **Student-uploaded PDFs** | Only source of truth for questions and grading |
| **Courses / topics / questions DB** | CRUD for course, topic, question, attempt |
| **Mastery store** | Per-topic score history driving the schedule |
| **Chroma index** | Retrieve the right page chunk for generating and grading |
| **LLM API** | Question writing and answer grading |

No web search: grading must come from the student's own material, not the internet. No LMS integrations in Phase 3.

## 6. Milestone plan (~3.5 weeks)

| Week | Milestone | Testable outcome |
|---|---|---|
| **W1** | Courses + PDF ingest | Auth, create course, upload PDFs, extract text by page, store chunks in Chroma; API tests for upload/validation |
| **W2** | Topics + questions | Curriculum worker produces topics; quiz worker generates ≥5 questions per topic, each with `source_page`; schema-validated |
| **W3** | Grading + adaptive plan | Grader scores free-text answers with missing points; mastery updates; next session prioritizes low-mastery topics (unit-tested scheduler) |
| **W3.5** | Dashboard + demo | Mastery chart, exam countdown, traces view; lint/tests green; 3-minute demo with one real lecture PDF |

## 7. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Grader is too harsh or too lenient | Students stop trusting scores | Grade against retrieved chunk only; show missing points + source page; allow "dispute" that logs for review |
| Bad questions from messy PDFs | Low-quality quizzes | Reject questions without a valid source page; let student flag/delete questions |
| LLM cost or outage | Demo fails | Cache generated questions; deterministic keyword-overlap grader as fallback |
| Scheduler feels random | Adaptive claim is weak | Simple, explainable rule (lowest mastery + longest since practiced) with unit tests |
| Scope creep (flashcard sharing, mobile, voice) | Miss deadline | One student, one course flow; everything else out of scope |

## Out of scope (Phase 3)

- Extending NotesLab  
- Sharing decks between students, classrooms, teacher dashboards  
- Web search or external content  
- Mobile app, voice answers, LMS sync  

## How this meets mentor approval criteria

| Criterion | Fit |
|---|---|
| **Feasibility (≤3 weeks, 1 person)** | One course flow: ingest → quiz → grade → reschedule |
| **Meaningful agentic AI** | Agent chooses what to ask, grades with grounding, and replans from memory |
| **Phase 1 + Phase 2** | Auth, forms, file upload, REST CRUD, SPA + file plugin, supervisor/workers, vector + KV memory, structured outputs, tracing |
| **Clear milestones** | Weekly pass/fail outcomes above |
| **Originality** | Grounded, adaptive grading of the student's own material, not a chatbot or notes app |
| **Scope** | Deep on one study loop, not a learning platform |

## Ask

Please approve **StudySprint** so Phase 3 can start with **W1 (courses + PDF ingest)**. I can revise within 48 hours based on feedback.
