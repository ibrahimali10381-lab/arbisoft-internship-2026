# 5-minute demo video script

**Setup before recording**
- Start the backend and frontend, or the deployed URL, on a fresh database so the demo course is newly seeded.
- Log in as `demo` / `demopass123`.
- Use a 1280×800 browser window, zoom 110%.
- Have `sample_data/os-lecture-week3.pdf` and one extra PDF of your own ready.

| Time | Screen | Say |
|---|---|---|
| 0:00–0:25 | Login page | "Rereading slides feels productive but doesn't tell you what you remember. StudySprint turns your own lecture PDFs into an adaptive quiz that grades you against the source." |
| 0:25–1:05 | Create a course → upload your own PDF | "I add a course with an exam date and upload a lecture. The curriculum agent extracts the text page by page and maps topics, each tied to the page it came from." Point at topics and page numbers. |
| 1:05–1:30 | Demo course page | "Here's a course I've already set up: four topics, mastery at zero, and a plan counting down to the exam, ending with a review day." |
| 1:30–2:40 | Start today's session | Answer Q1 well → **5/5**, mastery bar fills. Answer Q2 badly ("no idea") → low score, **missing points**, open **Source (page N)**. "The grader only uses the reference passage and key points from my PDF, and it tells me exactly what I missed." |
| 2:40–3:00 | Back to course page | "The weak topic now has low mastery and moves to the top of tomorrow's plan. That's the adaptive loop." |
| 3:00–3:30 | Ask your material: "What causes thrashing?" | "The secondary feature is RAG. Answers come only from my pages, with citations." Ask again: "(cached)". |
| 3:30–4:05 | Study agent: "Get me ready for the exam" → view trace | "A supervisor routes my goal to workers: curriculum, quiz, planner. Each step calls a registered tool, and every tool and model call is traced." Show the Traces page. |
| 4:05–4:40 | Compare models | "The same request goes to several models. Locally I have two offline graders; with keys, OpenAI and Groq show up here too. Every output is schema-validated, and invalid output is retried, then falls back to the next model." |
| 4:40–5:00 | README architecture diagram | "FastAPI, React, a model router with guards and fallback, 40 backend tests at 96% coverage, and one Docker container. Thanks!" |

**After recording:** export as 1080p MP4, upload to the program Google Drive folder, and paste the link into the README "Demo video" line.
