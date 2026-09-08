"""Supervisor agent: routes tasks to research / notes / file workers."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agent.hooks import traced_tool
from app.agent.workers import (
    WorkerResult,
    file_worker,
    notes_worker,
    research_worker,
)


@dataclass
class SupervisorResult:
    query: str
    route: list[str]
    handoffs: list[WorkerResult]
    answer: str


class SupervisorAgent:
    """
    Routes work to ≥2 sub-agents:
    - research_worker (SerpAPI)
    - notes_worker (local notes search)
    - file_worker (txt/pdf plugin)
    """

    name = "supervisor"

    @traced_tool(agent="supervisor", tool="route_task")
    def _choose_route(self, query: str) -> list[str]:
        q = query.lower()
        route: list[str] = []

        if any(token in q for token in ("note", "notes", "todo", "reminder")):
            route.append("notes_worker")
        if any(token in q for token in ("file", "pdf", "document", "readme", "brief")):
            route.append("file_worker")
        if any(
            token in q
            for token in ("search", "web", "research", "latest", "news", "what is", "who is")
        ):
            route.append("research_worker")

        # Multi-hop default: use notes + research when route is empty or single-intent vague.
        if not route:
            route = ["notes_worker", "research_worker"]
        if "and" in q and "research_worker" not in route:
            route.append("research_worker")
        if "and" in q and "notes_worker" not in route and "file" not in q:
            route.append("notes_worker")

        # Ensure uniqueness while preserving order
        seen: set[str] = set()
        ordered: list[str] = []
        for name in route:
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def run(
        self,
        *,
        query: str,
        db: Session,
        session_id: str = "default",
        owner_id: int | None = None,
        file_path: str | None = None,
    ) -> SupervisorResult:
        route = self._choose_route(query)
        handoffs: list[WorkerResult] = []

        for worker_name in route:
            if worker_name == "research_worker":
                handoffs.append(research_worker.run(query=query, session_id=session_id))
            elif worker_name == "notes_worker":
                handoffs.append(notes_worker.run(query=query, db=db, owner_id=owner_id))
            elif worker_name == "file_worker":
                path = file_path or "internship-brief.txt"
                handoffs.append(file_worker.run(relative_path=path))

        answer_parts = [
            f"Supervisor routed “{query}” to: {', '.join(route)}",
            "",
        ]
        for handoff in handoffs:
            answer_parts.append(f"### {handoff.worker}")
            answer_parts.append(handoff.summary)
            answer_parts.append("")

        return SupervisorResult(
            query=query,
            route=route,
            handoffs=handoffs,
            answer="\n".join(answer_parts).strip(),
        )


supervisor_agent = SupervisorAgent()
