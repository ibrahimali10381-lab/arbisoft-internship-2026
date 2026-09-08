"""Pre/post-action hooks that log every tool call with timestamps."""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from app.agent.tracing import TraceEvent, new_trace_id, trace_store, utc_now

F = TypeVar("F", bound=Callable[..., Any])


def _safe_preview(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_preview(item) for item in value[:5]]
    if isinstance(value, dict):
        return {str(k): _safe_preview(v) for k, v in list(value.items())[:10]}
    return f"<{type(value).__name__}>"


def traced_tool(agent: str, tool: str) -> Callable[[F], F]:
    """Decorator: pre-log → execute → post-log (or error log)."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            trace_id = new_trace_id()
            started = time.perf_counter()
            safe_args = {
                k: _safe_preview(v) for k, v in kwargs.items() if k not in {"self", "db"}
            }
            if args and not safe_args:
                safe_args = {"args_preview": [_safe_preview(a) for a in args[1:3]]}

            trace_store.add(
                TraceEvent(
                    id=trace_id,
                    timestamp=utc_now(),
                    agent=agent,
                    tool=tool,
                    phase="pre",
                    arguments=safe_args,
                )
            )

            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                trace_store.add(
                    TraceEvent(
                        id=new_trace_id(),
                        timestamp=utc_now(),
                        agent=agent,
                        tool=tool,
                        phase="error",
                        arguments=safe_args,
                        error=str(exc),
                        duration_ms=(time.perf_counter() - started) * 1000,
                        parent_trace_id=trace_id,
                    )
                )
                raise

            preview = result if isinstance(result, str) else repr(result)
            trace_store.add(
                TraceEvent(
                    id=new_trace_id(),
                    timestamp=utc_now(),
                    agent=agent,
                    tool=tool,
                    phase="post",
                    arguments=safe_args,
                    result_preview=preview[:500],
                    duration_ms=(time.perf_counter() - started) * 1000,
                    parent_trace_id=trace_id,
                )
            )
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
