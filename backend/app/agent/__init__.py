"""Research agent: planner → executor → memory loop."""

from __future__ import annotations

from dataclasses import dataclass

from app.agent.memory import MemoryStore, memory_store
from app.agent.skills import SearchHit, SerpApiSearchSkill


@dataclass
class ResearchResult:
    session_id: str
    query: str
    plan: list[str]
    answer: str
    sources: list[SearchHit]
    remembered_facts: list[str]
    memory_used: list[str]


class ResearchAgent:
    """
    Small composable agent:
    1. Plan steps for the query
    2. Recall session memory
    3. Execute SerpAPI web search skill
    4. Synthesize an answer and write new facts into memory
    """

    def __init__(
        self,
        *,
        search_skill: SerpApiSearchSkill | None = None,
        memory: MemoryStore | None = None,
    ) -> None:
        self.search_skill = search_skill or SerpApiSearchSkill()
        self.memory = memory or memory_store

    def _plan(self, query: str) -> list[str]:
        return [
            "Recall relevant facts from session memory",
            f"Search the web via SerpAPI for: {query}",
            "Synthesize an answer from memory + search hits",
            "Store concise findings back into session memory",
        ]

    def _synthesize(self, query: str, memory_used: list[str], sources: list[SearchHit]) -> str:
        lines = [f"Research summary for “{query}”:"]
        if memory_used:
            lines.append("From earlier in this session:")
            lines.extend(f"- {fact}" for fact in memory_used)
        if sources:
            lines.append("From SerpAPI web search:")
            for hit in sources:
                snippet = hit.snippet.strip() or "No snippet provided."
                lines.append(f"- {hit.title}: {snippet}")
        else:
            lines.append("No web results were available.")
        return "\n".join(lines)

    def run(self, *, query: str, session_id: str = "default") -> ResearchResult:
        plan = self._plan(query)
        memory_used = self.memory.recall(session_id, query=query)
        sources = self.search_skill.run(query)

        answer = self._synthesize(query, memory_used, sources)

        new_facts = [f"User researched: {query}"]
        for hit in sources[:3]:
            if hit.snippet:
                new_facts.append(f"{hit.title}: {hit.snippet[:180]}")

        for fact in new_facts:
            self.memory.remember(session_id, fact)

        return ResearchResult(
            session_id=session_id,
            query=query,
            plan=plan,
            answer=answer,
            sources=sources,
            remembered_facts=self.memory.all_facts(session_id),
            memory_used=memory_used,
        )


research_agent = ResearchAgent()
