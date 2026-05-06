"""Command-line entry point for the Research Summarizer Agent.

A thin wrapper around ``agent.summarize`` so workshop attendees can run the
agent without writing Python. The CLI does not add behavior — it only
formats output and maps the four documented exceptions to ``stderr`` lines
and a non-zero exit code.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

import anthropic

from agent.agent import summarize
from agent.models import SummaryResult
from agent.tools import NoResultsError, SearchToolError


def _format_text(result: SummaryResult) -> str:
    lines = [f"Topic: {result.topic}", "", f"Synopsis: {result.synopsis}", ""]
    lines.append("Key findings:")
    for i, finding in enumerate(result.key_findings, start=1):
        lines.append(f"  {i}. {finding}")
    lines.append("")
    lines.append("Citations:")
    for i, citation in enumerate(result.citations, start=1):
        lines.append(f"  [{i}] {citation.title}")
        lines.append(f"      {citation.url}")
        lines.append(f"      {citation.snippet}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-summarizer",
        description=(
            "Summarize a topic using web search and Claude. "
            "Reads ANTHROPIC_API_KEY and (optionally) TAVILY_API_KEY from "
            "the environment; without TAVILY_API_KEY the agent raises "
            "NoResultsError."
        ),
    )
    parser.add_argument("topic", help="The subject to research (non-empty).")
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Print the SummaryResult as indented JSON instead of plain text.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI. Returns the process exit code."""
    args = _build_parser().parse_args(argv)

    try:
        result = summarize(args.topic)
    except ValueError as exc:
        print(f"error: ValueError: {exc}", file=sys.stderr)
        return 1
    except NoResultsError as exc:
        print(f"error: NoResultsError: {exc or 'search returned no results'}", file=sys.stderr)
        return 1
    except SearchToolError as exc:
        print(f"error: SearchToolError: {exc}", file=sys.stderr)
        return 1
    except anthropic.APIError as exc:
        print(f"error: anthropic.APIError: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(result.model_dump_json(indent=2))
    else:
        print(_format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
