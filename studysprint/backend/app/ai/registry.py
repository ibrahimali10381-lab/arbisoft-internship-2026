from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.ai.tracing import traces


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def tool(self, name: str, description: str) -> Callable[[Callable], Callable]:
        def decorator(fn: Callable) -> Callable:
            if name in self._tools:
                raise ValueError(f"tool {name} already registered")
            self._tools[name] = Tool(name, description, fn)
            return fn

        return decorator

    def call(self, name: str, **kwargs: Any) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"unknown tool {name}")
        args = {k: v for k, v in kwargs.items() if k != "db"}
        with traces.span("tool", name, args=args) as span:
            result = tool.fn(**kwargs)
            span.note(result=result if isinstance(result, dict | list | str) else repr(result))
            return result

    def describe(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]


registry = ToolRegistry()
