"""Search tool interface and implementations.

The search tool is the sole external dependency and the primary mock boundary
for Level 1 tests. The protocol is intentionally narrow so test stubs can
substitute a controlled implementation without patching internals.
"""

from __future__ import annotations

import os
from typing import Protocol

from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SearchToolError(Exception):
    """Raised when the search tool fails (API error, timeout, network)."""


class NoResultsError(Exception):
    """Raised by ``summarize()`` when the search tool returns no results.

    The search tool itself returns an empty list rather than raising; the agent
    is responsible for raising this exception. That separation is what gives
    Level 1 tests a clean seam.
    """


class SearchTool(Protocol):
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Search for web results matching ``query``.

        Returns an empty list if no results are found (does NOT raise).
        Raises ``SearchToolError`` on API failure or timeout.
        """
        ...


class TavilySearchTool:
    """Real ``SearchTool`` implementation backed by the Tavily Search API.

    Reads ``TAVILY_API_KEY`` at construction time so missing-key errors surface
    early. A 10-second per-call timeout is enforced per the spec.
    """

    _TIMEOUT_SECONDS = 10.0

    def __init__(self, api_key: str | None = None) -> None:
        from tavily import TavilyClient

        key = api_key if api_key is not None else os.environ.get("TAVILY_API_KEY")
        if not key:
            raise SearchToolError("TAVILY_API_KEY is not set")
        self._client = TavilyClient(api_key=key)

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            response = self._client.search(
                query=query,
                max_results=max_results,
                timeout=self._TIMEOUT_SECONDS,
            )
        except Exception as exc:
            raise SearchToolError(f"Tavily search failed: {exc}") from exc

        raw_results = response.get("results", []) if isinstance(response, dict) else []
        return [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
            )
            for item in raw_results
        ]


class StubSearchTool:
    """Pre-configured ``SearchTool`` for tests and as a fallback.

    The constructor takes a fixed list of ``SearchResult`` objects; ``search()``
    returns that list verbatim regardless of query or ``max_results``.
    """

    def __init__(self, results: list[SearchResult]) -> None:
        self._results = list(results)

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return list(self._results)
