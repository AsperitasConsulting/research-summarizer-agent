"""Level 2 solution tests — instructor reference.

Level 2 tests exercise the agent end-to-end with a real Anthropic call. The
model is pinned and temperature is set to 0 so failures point at the agent
or the prompt, not at model variability.

These tests skip cleanly if either ``ANTHROPIC_API_KEY`` or
``TAVILY_API_KEY`` is missing.
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


def test_photosynthesis_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUMMARIZER_MODEL", TEST_MODEL)
    monkeypatch.setenv("SUMMARIZER_TEMPERATURE", str(TEST_TEMPERATURE))

    result = summarize("photosynthesis")

    assert len(result.key_findings) >= 2
    assert len(result.citations) >= 1


def test_result_fields_populated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUMMARIZER_MODEL", TEST_MODEL)
    monkeypatch.setenv("SUMMARIZER_TEMPERATURE", str(TEST_TEMPERATURE))

    stub = StubSearchTool(results=[
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
    ])

    result = summarize("photosynthesis", search_tool=stub)

    assert result.topic
    assert result.synopsis
    assert len(result.key_findings) >= 1
    assert len(result.citations) >= 1
