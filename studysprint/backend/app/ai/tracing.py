import time
import uuid
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

current_run_id: ContextVar[str | None] = ContextVar("current_run_id", default=None)


def _preview(value: Any, limit: int = 300) -> Any:
    if isinstance(value, str | int | float | bool) or value is None:
        return value[:limit] if isinstance(value, str) else value
    if isinstance(value, dict):
        return {str(k): _preview(v, limit) for k, v in list(value.items())[:12]}
    if isinstance(value, list | tuple):
        return [_preview(v, limit) for v in list(value)[:8]]
    return f"<{type(value).__name__}>"


@dataclass
class Span:
    kind: str
    name: str
    detail: dict[str, Any] = field(default_factory=dict)

    def note(self, **values: Any) -> None:
        self.detail.update({k: _preview(v) for k, v in values.items()})


class TraceStore:
    def __init__(self, max_events: int = 500) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)

    @contextmanager
    def span(self, kind: str, name: str, **detail: Any) -> Iterator[Span]:
        span = Span(kind=kind, name=name, detail={k: _preview(v) for k, v in detail.items()})
        started = datetime.now(UTC)
        start = time.perf_counter()
        status = "ok"
        try:
            yield span
        except Exception as exc:
            status = "error"
            span.note(error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            self._events.append(
                {
                    "id": uuid.uuid4().hex[:12],
                    "run_id": current_run_id.get(),
                    "kind": kind,
                    "name": name,
                    "status": status,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    "started_at": started,
                    "detail": span.detail,
                }
            )

    def list(self, limit: int = 100, run_id: str | None = None) -> list[dict[str, Any]]:
        events = [e for e in self._events if run_id is None or e["run_id"] == run_id]
        return list(reversed(events))[:limit]

    def clear(self) -> None:
        self._events.clear()


@contextmanager
def new_run() -> Iterator[str]:
    run_id = uuid.uuid4().hex[:10]
    token = current_run_id.set(run_id)
    try:
        yield run_id
    finally:
        current_run_id.reset(token)


traces = TraceStore()
