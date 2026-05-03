"""System prompt and user-message construction.

Prompt text is isolated here so it is easy to read, test, and modify. The
system prompt is reproduced verbatim from the spec; do not paraphrase.
"""

from __future__ import annotations

from agent.tools import SearchResult


SYSTEM_PROMPT = """You are a research assistant. Your job is to summarize information about a topic
based on web search results provided to you.

You must:
- Write a synopsis of 2-4 sentences covering the topic at a high level
- Identify 2-5 distinct key findings supported by the search results
- Cite at least one source per key finding using only URLs present in the
  provided search results

You must not:
- Invent facts not present in the search results
- Cite URLs that were not provided to you
- Express opinions or recommendations"""


def build_user_message(topic: str, results: list[SearchResult]) -> str:
    lines: list[str] = [f"Topic: {topic}", "", "Search Results:"]
    for index, result in enumerate(results, start=1):
        lines.append(f"[{index}] {result.title}")
        lines.append(f"URL: {result.url}")
        lines.append(result.snippet)
        lines.append("")
    lines.append("Return a structured summary following the required schema.")
    return "\n".join(lines)
