"""SerpAPI web-search skill for the research agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from serpapi import GoogleSearch

# Ensure backend/.env is loaded even if this module is imported before main.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass
class SearchHit:
    title: str
    link: str
    snippet: str


class SerpApiSearchSkill:
    """Composable web-search skill backed by SerpAPI Google results."""

    name = "web_search"
    description = "Search the public web with SerpAPI and return top organic results."

    def __init__(self, api_key: str | None = None) -> None:
        # Keep an explicit override if provided; otherwise read env lazily in run().
        self._api_key_override = api_key

    def _resolve_api_key(self) -> str:
        if self._api_key_override is not None:
            return self._api_key_override.strip()
        return (os.getenv("SERPAPI_API_KEY") or "").strip()

    def run(self, query: str, *, num: int = 10) -> list[SearchHit]:
        api_key = self._resolve_api_key()
        if not api_key:
            # Deterministic offline fallback so local demos/tests still work.
            return [
                SearchHit(
                    title=f"Demo result for: {query}",
                    link="https://example.com/demo-search",
                    snippet=(
                        "SERPAPI_API_KEY is not set. Returning a demo hit so the agent loop "
                        f"can still run for query '{query}'."
                    ),
                )
            ]

        search = GoogleSearch(
            {
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "num": num,
            }
        )
        payload = search.get_dict()
        if payload.get("error"):
            raise RuntimeError(str(payload["error"]))

        organic = payload.get("organic_results") or []
        if not organic:
            raise RuntimeError(
                "SerpAPI returned no organic results. Check your key, plan quota, or query."
            )

        hits: list[SearchHit] = []
        for item in organic[:num]:
            hits.append(
                SearchHit(
                    title=item.get("title") or "Untitled",
                    link=item.get("link") or "",
                    snippet=item.get("snippet") or "",
                )
            )
        return hits
