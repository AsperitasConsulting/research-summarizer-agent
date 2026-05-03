"""Research Summarizer Agent — workshop teaching vehicle."""

from agent.agent import summarize
from agent.models import Citation, SummaryResult
from agent.tools import (
    NoResultsError,
    SearchResult,
    SearchTool,
    SearchToolError,
    StubSearchTool,
)

__all__ = [
    "summarize",
    "SummaryResult",
    "Citation",
    "SearchTool",
    "StubSearchTool",
    "SearchResult",
    "SearchToolError",
    "NoResultsError",
]
