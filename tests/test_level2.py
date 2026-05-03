"""Level 2 tests — workshop starter file.

Level 2 in the AI Agent Testing Pyramid is the **constrained-model** band.
We pin the model name and set the temperature to 0 so behavior is as
deterministic as a stochastic system can be, then run the agent end-to-end
against the real Anthropic API. Failures here point at agent or prompt
problems, not at model variability.

Why pin the model and temperature?

* **Model pin** (`claude-haiku-4-5-20251001`): aliased model names like
  ``claude-haiku-latest`` can silently change behavior between today and
  workshop day. Pinning gives us a stable target.
* **Temperature 0**: removes most sampling randomness. The model still has
  some non-determinism, but assertions can rely on coarse structural
  properties (counts, presence of fields) rather than exact strings.

These tests cost real Anthropic and Tavily quota. Run them sparingly —
your free-tier budget is finite.
"""

from __future__ import annotations

import os

import pytest

from agent import SearchResult, StubSearchTool, summarize


TEST_MODEL = "claude-haiku-4-5-20251001"
TEST_TEMPERATURE = 0


pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get("TAVILY_API_KEY"),
    reason="Level 2 tests require ANTHROPIC_API_KEY and TAVILY_API_KEY",
)


# def test_photosynthesis_summary(monkeypatch):
#     # Why this test is Level 2: it calls the real Anthropic API and the real
#     # Tavily search API. The model and temperature are pinned via
#     # monkeypatch.setenv() so the agent reads them as if they were in your .env.
#     #
#     # Arrange: monkeypatch SUMMARIZER_MODEL = TEST_MODEL,
#     #                       SUMMARIZER_TEMPERATURE = str(TEST_TEMPERATURE).
#     # Act:     call summarize("photosynthesis").
#     # Assert:  the result has at least 2 key_findings and at least 1 citation.
#     pass


# def test_result_fields_populated(monkeypatch):
#     # Why this test is Level 2: it calls the real Anthropic API but uses
#     # StubSearchTool for the search side. That makes the search dimension
#     # deterministic (same inputs every time) while still exercising the
#     # model on its summarization dimension.
#     #
#     # Arrange: monkeypatch SUMMARIZER_MODEL and SUMMARIZER_TEMPERATURE as above.
#     #          Build a StubSearchTool with two SearchResult objects (any topic).
#     # Act:     call summarize("photosynthesis", search_tool=<your stub>).
#     # Assert:  result.topic, result.synopsis are non-empty;
#     #          len(result.key_findings) >= 1; len(result.citations) >= 1.
#     pass
