"""Routes each AI task across models with schema validation, retry, fallback and caching."""

import hashlib
import json
import os
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError

from app.ai.outputs import Guard, GuardError
from app.ai.providers import (
    LocalProvider,
    OpenAICompatibleProvider,
    Provider,
    ProviderError,
)
from app.ai.tracing import traces
from app.config import settings


class AIUnavailableError(RuntimeError):
    pass


@dataclass
class RoutedResult:
    output: BaseModel
    model: str
    cached: bool
    attempts: list[dict[str, Any]] = field(default_factory=list)


class ModelRouter:
    def __init__(
        self,
        providers: list[Provider],
        priority: list[str],
        max_retries: int = 1,
        cache_size: int = 256,
    ) -> None:
        self.providers = {p.id: p for p in providers}
        self.priority = priority
        self.max_retries = max_retries
        self.cache_size = cache_size
        self._cache: OrderedDict[str, BaseModel] = OrderedDict()

    def available(self) -> list[str]:
        return [pid for pid, p in self.providers.items() if p.available]

    def chain(self, preferred: str | None = None) -> list[str]:
        order = ([preferred] if preferred else []) + self.priority + ["local-keyword"]
        seen: list[str] = []
        for pid in order:
            p = self.providers.get(pid)
            if p is not None and p.available and pid not in seen:
                seen.append(pid)
        return seen

    def clear_cache(self) -> None:
        self._cache.clear()

    def _cache_key(self, task: str, model: str, payload: dict[str, Any]) -> str:
        raw = json.dumps([task, model, payload], sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _call_once(
        self,
        provider: Provider,
        task: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        guard: Guard | None,
    ) -> BaseModel:
        raw = provider.run(task, payload, schema)
        data = json.loads(raw) if isinstance(raw, str) else raw
        output = schema.model_validate(data)
        if guard:
            guard(output)
        return output

    def run_on(
        self,
        model: str,
        task: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        guard: Guard | None = None,
        attempts: list[dict[str, Any]] | None = None,
    ) -> BaseModel:
        provider = self.providers.get(model)
        if provider is None or not provider.available:
            raise ProviderError(f"model {model} is not available")
        attempts = attempts if attempts is not None else []
        request = payload
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            with traces.span("model", f"{task}:{model}", attempt=attempt + 1) as span:
                try:
                    output = self._call_once(provider, task, request, schema, guard)
                    attempts.append({"model": model, "attempt": attempt + 1, "ok": True})
                    span.note(output=output.model_dump())
                    return output
                except (ValidationError, GuardError, json.JSONDecodeError) as exc:
                    last_error = exc
                    attempts.append({"model": model, "attempt": attempt + 1, "ok": False})
                    span.note(rejected=str(exc)[:300])
                    request = {**payload, "_previous_output_was_invalid": str(exc)[:500]}
        raise ProviderError(f"{model} returned invalid output: {last_error}")

    def run(
        self,
        task: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        guard: Guard | None = None,
        model: str | None = None,
        use_cache: bool = True,
    ) -> RoutedResult:
        attempts: list[dict[str, Any]] = []
        errors: list[str] = []
        for pid in self.chain(model):
            key = self._cache_key(task, pid, payload)
            if use_cache and key in self._cache:
                self._cache.move_to_end(key)
                with traces.span("cache", f"{task}:{pid}", hit=True):
                    pass
                return RoutedResult(self._cache[key], pid, True, attempts)
            try:
                output = self.run_on(pid, task, payload, schema, guard, attempts)
            except ProviderError as exc:
                errors.append(str(exc))
                continue
            if use_cache:
                self._cache[key] = output
                if len(self._cache) > self.cache_size:
                    self._cache.popitem(last=False)
            return RoutedResult(output, pid, False, attempts)
        raise AIUnavailableError("; ".join(errors) or "no model available")

    def compare(
        self,
        task: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        guard: Guard | None = None,
        models: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        rows = []
        for pid in models or self.available():
            start = time.perf_counter()
            try:
                output = self.run_on(pid, task, payload, schema, guard)
                rows.append({"model": pid, "ok": True, "output": output.model_dump()})
            except ProviderError as exc:
                rows.append({"model": pid, "ok": False, "error": str(exc)})
            rows[-1]["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        return rows


def build_default_router() -> ModelRouter:
    providers: list[Provider] = [
        OpenAICompatibleProvider(
            "openai",
            "OpenAI",
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            os.getenv("OPENAI_API_KEY"),
        ),
        OpenAICompatibleProvider(
            "groq",
            "Groq",
            "https://api.groq.com/openai/v1",
            os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            os.getenv("GROQ_API_KEY"),
        ),
        OpenAICompatibleProvider(
            "ollama",
            "Ollama",
            os.getenv("OLLAMA_BASE_URL"),
            os.getenv("OLLAMA_MODEL", "llama3.2"),
            requires_key=False,
            timeout=60.0,
        ),
        LocalProvider("keyword"),
        LocalProvider("semantic"),
    ]
    return ModelRouter(providers, settings.model_priority)


router = build_default_router()
