"""Multi-hop single-agent demo: chains memory, file read, and web search."""

from __future__ import annotations

from dataclasses import dataclass

from app.agent import research_agent
from app.agent.hooks import traced_tool
from app.agent.memory import memory_store
from app.agent.plugins.file_read import file_read_plugin


@dataclass
class MultiHopResult:
    question: str
    steps: list[str]
    answer: str
    session_id: str


class MultiHopAgent:
    """
    Demo agent for Week 4:
    1) read a local brief
    2) remember key facts
    3) run a follow-up web search that uses memory
    """

    name = "multi_hop_agent"

    @traced_tool(agent="multi_hop_agent", tool="multi_hop_demo")
    def run(self, question: str, session_id: str = "multi-hop") -> MultiHopResult:
        steps: list[str] = []

        steps.append("Read internship-brief.txt via file-read plugin")
        brief = file_read_plugin.read("internship-brief.txt")
        memory_store.remember(session_id, f"Brief excerpt: {brief[:240]}")

        steps.append("Store brief facts in session memory")
        memory_store.remember(session_id, f"User multi-hop question: {question}")

        steps.append("Run SerpAPI research using recalled memory")
        research = research_agent.run(query=question, session_id=session_id)

        answer = (
            "Multi-hop answer\n"
            f"1) Local brief used ({len(brief)} chars)\n"
            f"2) Memory facts: {len(research.memory_used)}\n"
            f"3) Web synthesis:\n{research.answer}"
        )
        steps.append("Synthesize final multi-hop response")

        return MultiHopResult(
            question=question,
            steps=steps,
            answer=answer,
            session_id=session_id,
        )


multi_hop_agent = MultiHopAgent()
