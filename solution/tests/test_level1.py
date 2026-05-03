"""Level 1 solution tests — instructor reference.

Level 1 tests exercise orchestration logic in isolation: input validation,
tool injection, and exception propagation. They use ``StubSearchTool`` for
the search side and never call the Anthropic API, so they run fast and are
fully deterministic.

The defect-catching test (`test_no_results_raises_no_results_error`) is the
one that fails against the seeded-defect version of the agent.
"""

from __future__ import annotations

import pytest

from agent import (
    NoResultsError,
    SearchResult,
    SearchToolError,
    StubSearchTool,
    summarize,
)


@pytest.fixture
def stub_results() -> list[SearchResult]:
    return [
        SearchResult(
            title="Photosynthesis Overview",
            url="https://en.wikipedia.org/wiki/Photosynthesis",
            snippet="Photosynthesis converts light energy into chemical energy.",
        ),
        SearchResult(
            title="Calvin Cycle",
            url="https://www.ncbi.nlm.nih.gov/books/NBK10/",
            snippet="The Calvin cycle fixes carbon dioxide into carbohydrates.",
        ),
    ]


def test_empty_topic_raises_value_error() -> None:
    with pytest.raises(ValueError):
        summarize("")


def test_no_results_raises_no_results_error() -> None:
    empty_tool = StubSearchTool(results=[])
    with pytest.raises(NoResultsError):
        summarize("anything", search_tool=empty_tool)


def test_search_tool_error_propagates() -> None:
    class RaisingTool:
        def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
            raise SearchToolError("simulated tool failure")

    with pytest.raises(SearchToolError):
        summarize("anything", search_tool=RaisingTool())
