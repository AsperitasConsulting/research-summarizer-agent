"""Shared LLM-as-judge helpers for Level 3 evaluation.

This module factors out the rubric, prompt builders, and judge invocation
that ``evals/judge_eval.py`` originally inlined, so that ``tests/test_level3.py``
can reuse exactly the same judge contract.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic


JUDGE_MODEL = "claude-sonnet-4-6"


JUDGE_SYSTEM_PROMPT = """You are an evaluation judge. You will be given:
- A research topic
- The exact search results that were provided to a summarizer agent
- The summarizer agent's structured output (synopsis, key findings, citations)

You must grade the agent's output on four pass/fail dimensions and return
a single JSON object with the verdicts. Do not include prose outside the JSON."""


JUDGE_RUBRIC_INSTRUCTIONS = """Grade the following four dimensions, each as "pass" or "fail":

1. factual_accuracy
   - The synopsis and every key finding must be supported by, or consistent
     with, the cited search-result snippets. Inventing facts or contradicting
     the snippets is a fail.

2. citation_integrity
   - Every URL listed in the agent's citations must appear in the URL list of
     the search results provided to it. Any citation URL not present in the
     search results is a fail.

3. synopsis_quality
   - The synopsis must be 2-4 sentences, on-topic, and free of opinions or
     recommendations. Anything outside that band is a fail.

4. findings_count
   - The agent must list 2-5 substantive findings. Fewer than 2 or more than 5
     is a fail. Findings that are duplicative or trivially restate the
     synopsis are also a fail.

Return your answer as a single JSON object with this exact shape:
{
  "factual_accuracy": "pass" | "fail",
  "citation_integrity": "pass" | "fail",
  "synopsis_quality": "pass" | "fail",
  "findings_count": "pass" | "fail",
  "comments": "<one short sentence per dimension explaining the verdict>"
}"""


RUBRIC_DIMENSIONS = (
    "factual_accuracy",
    "citation_integrity",
    "synopsis_quality",
    "findings_count",
)


def build_judge_prompt(
    topic: str, search_results: list[dict], agent_result: dict
) -> str:
    return (
        f"Topic: {topic}\n\n"
        f"Search results provided to the agent:\n"
        f"{json.dumps(search_results, indent=2)}\n\n"
        f"Agent output:\n"
        f"{json.dumps(agent_result, indent=2)}\n\n"
        f"{JUDGE_RUBRIC_INSTRUCTIONS}"
    )


def extract_text(response: anthropic.types.Message) -> str:
    """Concatenate the text from response.content text-blocks only."""
    return "".join(b.text for b in response.content if getattr(b, "type", None) == "text")


def parse_judge_verdicts(raw: str) -> tuple[dict, str]:
    """Pull the JSON object out of the judge's text and return (verdicts, comments)."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Judge response did not contain a JSON object:\n{raw}")
    parsed = json.loads(raw[start : end + 1])
    comments = parsed.pop("comments", "")
    return parsed, comments


def run_judge(
    topic: str,
    search_results: list[dict],
    agent_result: dict,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = JUDGE_MODEL,
    max_tokens: int = 1024,
) -> tuple[dict, str, str]:
    """Call the judge model and return (verdicts, comments, raw_text)."""
    prompt = build_judge_prompt(topic, search_results, agent_result)
    api = client if client is not None else anthropic.Anthropic()
    response = api.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = extract_text(response)
    verdicts, comments = parse_judge_verdicts(raw)
    return verdicts, comments, raw


__all__ = [
    "JUDGE_MODEL",
    "JUDGE_SYSTEM_PROMPT",
    "JUDGE_RUBRIC_INSTRUCTIONS",
    "RUBRIC_DIMENSIONS",
    "build_judge_prompt",
    "extract_text",
    "parse_judge_verdicts",
    "run_judge",
]
