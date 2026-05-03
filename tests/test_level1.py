"""Level 1 tests — workshop starter file.

Level 1 in the AI Agent Testing Pyramid is the unit-test base: fast,
deterministic, and reliant on mocks/stubs. Here we use the agent's built-in
``StubSearchTool`` to control what the search side returns, so we can test
the agent's orchestration logic without ever calling the Anthropic API.

Pytest fundamentals you will see in this file:

* ``@pytest.fixture`` — a reusable piece of test setup. The
  ``stub_results`` fixture below builds a list of fake search results that
  any test can request by listing it as a parameter.
* ``pytest.raises(...)`` — a context manager that asserts the wrapped
  block raises a specific exception. This is the standard way to test
  error paths.
* Arrange / Act / Assert — every test reads top-to-bottom in three
  short blocks: build inputs, call the function under test, check the
  result (or that the right exception was raised).

Workshop goal: fill in the two commented-out test stubs below so all three
tests pass against the **corrected** agent and the second stub fails
against the **defective** agent (the one with the ``# TODO: handle empty
results`` marker still in ``agent/agent.py``).
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
    """Two pre-built ``SearchResult`` objects for tests that need a non-empty stub."""
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
    """The agent must reject empty/whitespace-only topics with ``ValueError``.

    This test is fully written and should pass against both the corrected
    and defective agent. It is the model your two stubs below are based on.
    """
    with pytest.raises(ValueError):
        summarize("")


# def test_no_results_raises_no_results_error():
#     # Hint: see the `# TODO: handle empty results` marker in agent/agent.py.
#     # Arrange: build a StubSearchTool whose results list is empty.
#     # Act:     call summarize(...) with that tool injected via search_tool=.
#     # Assert:  pytest.raises(NoResultsError) wraps the call.
#     pass


# def test_search_tool_error_propagates():
#     # Arrange: build a stub class whose .search() raises SearchToolError.
#     #          (StubSearchTool does not raise; you'll need a tiny class of
#     #          your own — any object with a .search(query, max_results) method
#     #          satisfies the SearchTool protocol.)
#     # Act:     call summarize(...) with that tool injected via search_tool=.
#     # Assert:  pytest.raises(SearchToolError) wraps the call.
#     pass
