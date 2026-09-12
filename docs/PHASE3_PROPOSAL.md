# Phase 3 Project Proposal — ClaimCheck

**Intern:** Ibrahim Ali  
**Program:** Arbisoft AI-Focused Internship Program 2026  
**Gate:** End of mid-Week 5 — mentor approval required before Phase 3 build  
**Date:** 2026-09-12  
**Status:** Draft for mentor review

> Phase 3 development will not start until this proposal is approved. I can revise within 48 hours based on feedback.

---

## 1. Problem statement

People constantly encounter bold claims in headlines, social posts, and marketing copy, but verifying them means opening many tabs, skimming unrelated results, and guessing which sources are trustworthy. Casual users rarely produce a clear verdict with evidence, and generic chatbots often answer confidently without showing a transparent tool trail. There is no small, focused web app that takes one claim, runs a supervised multi-agent evidence check, and returns a cited verdict with visible traces.

## 2. Target users and core use case

**Target users**
- Students and interns evaluating online claims for assignments or discussions  
- Curious readers who want a fast “is this supported?” check before sharing  
- Mentors/demo audiences who need a clear agentic AI walkthrough

**Core use case**  
A user pastes: *“Drinking coffee permanently stunts growth in teenagers.”*  
ClaimCheck:
1. extracts a normalized claim,  
2. searches the web for supporting/refuting evidence (SerpAPI),  
3. scores confidence and stance,  
4. returns a **Verdict Card** (Supported / Mixed / Unsupported / Insufficient evidence) with 3–5 citations and a short explanation,  
5. logs every tool call so the user can see how the answer was produced.

## 3. Key AI feature(s) (agent primitives)

**Primary feature — Agentic Claim Verification Pipeline**

| Primitive | Role in ClaimCheck |
|---|---|
| **Supervisor + workers** | Routes to claim-normalizer, evidence-researcher, and verdict-writer (≥2 workers) |
| **Skills / tools** | SerpAPI web search; optional URL fetch for a single source page; schema-validated verdict output |
| **Hooks + tracing** | Timestamped pre/post logs for every tool call (demo + debugging) |
| **Memory** | Session memory of claims already checked (avoid duplicate searches; compare related claims) |
| **ReAct / multi-hop** | Normalize → search → read top results → revise verdict if evidence conflicts |
| **MCP (stretch)** | `verify_claim(text)` tool for Cursor / custom client |

No note-taking, journals, or personal knowledge base — the product is claim → evidence → verdict.

## 4. Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite + TypeScript |
| Backend | FastAPI + SQLAlchemy + JWT (saved history optional, not a notes product) |
| LLM | OpenAI-compatible API for claim normalization + verdict synthesis |
| Web evidence | SerpAPI |
| Validation | Pydantic structured outputs for `VerdictCard` |
| Observability | Custom trace store + hooks |
| Quality | pytest, Vitest, ruff, ESLint, `prompts.md` |

## 5. Data sources / integrations needed

| Source | Purpose |
|---|---|
| User-submitted claim text | Primary input |
| Optional article URL | Extract the main claim from a page |
| SerpAPI | Retrieve supporting/refuting sources |
| LLM API | Normalize claim, rank evidence, draft verdict explanation |
| Session/run store | History of verifications for the signed-in user (list of past verdicts, not freeform notes) |

No Google Docs, Notion, email, or note apps.

## 6. Milestone plan (~3.5 weeks)

| Week | Milestone | Testable outcome |
|---|---|---|
| **W1** | Auth + Claim submit UI + Verdict schema | User submits a claim; API returns a validated empty/skeleton `VerdictCard`; tests for schema + auth |
| **W2** | Multi-agent evidence pipeline | Supervisor runs ≥2 workers; SerpAPI results attached; traces visible in UI |
| **W3** | Scoring + citations UX | Verdict labels work on a fixed 10-claim eval set; each verdict shows citations + confidence |
| **W3.5** | Hardening + mentor demo | Fallback mode without API keys; lint/tests green; demo script + MCP stretch if time |

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated citations | Only cite URLs returned by SerpAPI; never invent links |
| Sensitive/medical/legal claims | UI disclaimer: educational tool, not professional advice; refuse clearly disallowed categories if needed |
| API cost / key failure | Stub evidence fixtures for CI; demo mode with cached sample claims |
| Ambiguous claims | Normalizer asks for clarification or splits into atomic claims |
| Over-ambition (full fact-checking platform) | Cap v1 to single-claim text/URL input; no browser extension, no social feed monitor |

## Out of scope (Phase 3)

- Real-time social media monitoring  
- Browser extension  
- Community voting / wiki of claims  
- Note-taking, journaling, or personal knowledge management  
- Reusing NotesLab as the product shell (portfolio code patterns may be reused; product is separate)

## How this meets mentor approval criteria

| Criterion | Fit |
|---|---|
| **Feasibility** | One workflow, known stack, weekly demos |
| **Meaningful agentic AI** | Supervisor/workers + tools + memory + traces producing a verdict artifact |
| **Phase 1 + Phase 2** | Web app auth/CRUD-style history (Phase 1) + agents/skills/hooks/MCP (Phase 2) |
| **Clear milestones** | Each week has a pass/fail demo |
| **Originality** | Focused claim verifier, not a ChatGPT clone or todo/notes tutorial |
| **Scope** | Single claim in → verdict out; intentionally narrow |


