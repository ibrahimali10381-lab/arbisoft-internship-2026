"""In-session memory for the research agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class MemoryStore:
    """Simple session memory that persists facts for the lifetime of the process."""

    _sessions: dict[str, list[str]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def remember(self, session_id: str, fact: str) -> None:
        cleaned = fact.strip()
        if not cleaned:
            return
        with self._lock:
            facts = self._sessions.setdefault(session_id, [])
            if cleaned not in facts:
                facts.append(cleaned)

    def recall(self, session_id: str, query: str | None = None, limit: int = 8) -> list[str]:
        with self._lock:
            facts = list(self._sessions.get(session_id, []))

        if not query:
            return facts[-limit:]

        tokens = {token.lower() for token in query.split() if len(token) > 2}
        ranked: list[tuple[int, str]] = []
        for fact in facts:
            score = sum(1 for token in tokens if token in fact.lower())
            ranked.append((score, fact))

        ranked.sort(key=lambda item: (-item[0], facts.index(item[1])))
        relevant = [fact for score, fact in ranked if score > 0]
        if relevant:
            return relevant[:limit]
        return facts[-limit:]

    def all_facts(self, session_id: str) -> list[str]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


memory_store = MemoryStore()
