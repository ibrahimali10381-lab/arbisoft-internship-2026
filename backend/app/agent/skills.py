"""SerpAPI web-search skill for the research agent."""

from __future__ import annotations

import os
from dataclasses import dataclass

from serpapi import GoogleSearch


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
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY", "")

    def run(self, query: str, *, num: int = 5) -> list[SearchHit]:
        if not self.api_key:
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
                "api_key": self.api_key,
                "engine": "google",
                "num": num,
            }
        )
        payload = search.get_dict()
        if payload.get("error"):
            raise RuntimeError(str(payload["error"]))

        hits: list[SearchHit] = []
        for item in payload.get("organic_results", [])[:num]:
            hits.append(
                SearchHit(
                    title=item.get("title") or "Untitled",
                    link=item.get("link") or "",
                    snippet=item.get("snippet") or "",
                )
            )
        return hits
