"""Agent runner: a supervisor routes a student's goal to specialised workers."""

import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

import app.ai.tools  # noqa: F401  (registers tools)
from app.ai.registry import registry
from app.ai.tracing import new_run, traces
from app.models import Course, Topic, User


@dataclass
class AgentContext:
    db: Session
    course: Course
    user: User
    goal: str
    steps: list[dict[str, str]] = field(default_factory=list)
    output: dict[str, Any] = field(default_factory=dict)
    stop: bool = False

    def log(self, worker: str, tool: str, summary: str) -> None:
        self.steps.append({"worker": worker, "tool": tool, "summary": summary})


class CurriculumWorker:
    name = "curriculum_worker"

    def handle(self, ctx: AgentContext) -> None:
        if not ctx.course.documents:
            ctx.log(self.name, "-", "No material uploaded yet; upload a PDF to start.")
            ctx.output["message"] = "Upload course material first."
            ctx.stop = True
            return
        if not ctx.course.topics:
            for doc in ctx.course.documents:
                pages: dict[int, list[str]] = {}
                for chunk in doc.chunks:
                    pages.setdefault(chunk.page, []).append(chunk.text)
                registry.call(
                    "extract_topics",
                    db=ctx.db,
                    course=ctx.course,
                    document=doc,
                    pages=[(p, "\n\n".join(t)) for p, t in sorted(pages.items())],
                )
            ctx.db.commit()
            ctx.db.refresh(ctx.course)
            ctx.log(self.name, "extract_topics", f"Rebuilt {len(ctx.course.topics)} topics.")
        else:
            ctx.log(self.name, "-", f"{len(ctx.course.topics)} topics already mapped.")
        ctx.output["topics"] = [t.name for t in ctx.course.topics]


class QuizWorker:
    name = "quiz_worker"

    def handle(self, ctx: AgentContext) -> None:
        thin: list[Topic] = [t for t in ctx.course.topics if len(t.questions) < 2]
        created = 0
        for topic in thin:
            result = registry.call("generate_questions", db=ctx.db, topic=topic, count=3)
            created += result["created"]
        ctx.log(
            self.name,
            "generate_questions",
            f"Generated {created} questions across {len(thin)} topics."
            if thin
            else "Every topic already has questions.",
        )
        ctx.output["questions_created"] = created


class SessionWorker:
    name = "session_worker"

    def handle(self, ctx: AgentContext) -> None:
        questions = registry.call(
            "build_session", db=ctx.db, course=ctx.course, user=ctx.user, size=5
        )
        ctx.log(self.name, "build_session", f"Picked {len(questions)} questions, weakest first.")
        ctx.output["session"] = [
            {"question_id": q.id, "topic": q.topic.name, "prompt": q.prompt} for q in questions
        ]


class PlannerWorker:
    name = "planner_worker"

    def handle(self, ctx: AgentContext) -> None:
        plan = registry.call("plan_sessions", course=ctx.course)
        ctx.log(self.name, "plan_sessions", f"Planned {len(plan)} study days.")
        ctx.output["plan"] = [{**day, "date": day["date"].isoformat()} for day in plan]


class TutorWorker:
    name = "tutor_worker"

    def handle(self, ctx: AgentContext) -> None:
        result = registry.call("answer_question", db=ctx.db, course=ctx.course, question=ctx.goal)
        pages = ", ".join(str(c["page"]) for c in result["citations"]) or "none"
        ctx.log(self.name, "answer_question", f"Answered with {result['model']}; pages {pages}.")
        ctx.output["answer"] = result


_ASK_RE = re.compile(r"^(what|why|how|explain|define|describe|who|when|which|compare)\b", re.I)

PIPELINES = {
    "prepare": [CurriculumWorker, QuizWorker, PlannerWorker],
    "quiz": [CurriculumWorker, QuizWorker, SessionWorker],
    "plan": [CurriculumWorker, PlannerWorker],
    "ask": [TutorWorker],
}


class Supervisor:
    def route(self, goal: str) -> str:
        text = goal.strip().lower()
        if re.search(r"\b(quiz|test me|practice|questions?)\b", text):
            return "quiz"
        if re.search(r"\b(plan|schedule|timetable)\b", text):
            return "plan"
        if text.endswith("?") or _ASK_RE.match(text):
            return "ask"
        return "prepare"

    def run(self, db: Session, course: Course, user: User, goal: str) -> dict[str, Any]:
        with new_run() as run_id:
            intent = self.route(goal)
            ctx = AgentContext(db=db, course=course, user=user, goal=goal)
            with traces.span("agent", "supervisor", goal=goal, intent=intent):
                for worker_cls in PIPELINES[intent]:
                    worker = worker_cls()
                    with traces.span("worker", worker.name):
                        worker.handle(ctx)
                    if ctx.stop:
                        break
            return {"run_id": run_id, "intent": intent, "steps": ctx.steps, "output": ctx.output}


supervisor = Supervisor()
