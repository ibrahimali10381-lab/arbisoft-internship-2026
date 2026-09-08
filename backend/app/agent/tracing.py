"""Tracing layer for tool calls across the agent graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any
from uuid import uuid4


@dataclass
class TraceEvent:
    id: str
    timestamp: str
    agent: str
    tool: str
    phase: str  # pre | post | error
    arguments: dict[str, Any]
    result_preview: str | None = None
    error: str | None = None
    duration_ms: float | None = None
    parent_trace_id: str | None = None


@dataclass
class TraceStore:
    _events: list[TraceEvent] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def add(self, event: TraceEvent) -> TraceEvent:
        with self._lock:
            self._events.append(event)
            return event

    def list_events(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            events = list(self._events[-limit:])
        serialized: list[dict[str, Any]] = []
        for event in events:
            serialized.append(
                {
                    "id": event.id,
                    "timestamp": event.timestamp,
                    "agent": event.agent,
                    "tool": event.tool,
                    "phase": event.phase,
                    "arguments": event.arguments,
                    "result_preview": event.result_preview,
                    "error": event.error,
                    "duration_ms": event.duration_ms,
                    "parent_trace_id": event.parent_trace_id,
                }
            )
        return serialized

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


trace_store = TraceStore()


def new_trace_id() -> str:
    return uuid4().hex


def utc_now() -> str:
    return datetime.now(UTC).isoformat()
