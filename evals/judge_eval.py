"""LLM-as-judge demo for the Research Summarizer Agent.

Workshop role: Segment 5. The instructor runs this live during the session;
attendees can run it themselves afterwards. The script:

1. Calls ``summarize()`` on a hard-coded topic ("the discovery of penicillin").
2. Captures the search results that were passed to the agent (so the judge
   can verify citation provenance).
3. Asks a separate, more capable model (``claude-sonnet-4-6``) to grade the
   agent's output on four pass/fail rubric dimensions.
4. Prints a labelled report to stdout and writes a JSON trace to
   ``sample_outputs/judge_eval_run.json``.

The trace is committed to the repo as a known-good example run. Re-run this
script after prompt or pin changes and commit the new trace.

Run with::

    python evals/judge_eval.py

Both ``ANTHROPIC_API_KEY`` and ``TAVILY_API_KEY`` must be set.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv


_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from agent import StubSearchTool, summarize  # noqa: E402
from agent.tools import TavilySearchTool  # noqa: E402


load_dotenv()


# Pinned models. Do not swap to aliases — the workshop teaches model pinning.
AGENT_MODEL = "claude-haiku-4-5-20251001"
JUDGE_MODEL = "claude-sonnet-4-6"
TOPIC = "the discovery of penicillin"

OUTPUT_PATH = _REPO_ROOT / "sample_outputs" / "judge_eval_run.json"


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


def _build_judge_prompt(topic: str, search_results: list[dict], agent_result: dict) -> str:
    return (
        f"Topic: {topic}\n\n"
        f"Search results provided to the agent:\n"
        f"{json.dumps(search_results, indent=2)}\n\n"
        f"Agent output:\n"
        f"{json.dumps(agent_result, indent=2)}\n\n"
        f"{JUDGE_RUBRIC_INSTRUCTIONS}"
    )


def _extract_text(response: anthropic.types.Message) -> str:
    """Concatenate the text from response.content text-blocks only."""
    return "".join(b.text for b in response.content if getattr(b, "type", None) == "text")


def _parse_judge_verdicts(raw: str) -> tuple[dict, str]:
    """Pull the JSON object out of the judge's text and return (verdicts, comments)."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Judge response did not contain a JSON object:\n{raw}")
    parsed = json.loads(raw[start : end + 1])
    comments = parsed.pop("comments", "")
    return parsed, comments


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("TAVILY_API_KEY"):
        print("ERROR: TAVILY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    # Run the search ourselves so we have a record of exactly what was passed
    # to the agent (the agent does not expose its search results).
    search_tool = TavilySearchTool()
    search_results = search_tool.search(TOPIC, max_results=5)
    search_results_payload = [r.model_dump() for r in search_results]

    # Re-inject the same search results into the agent via StubSearchTool, so
    # the judge sees exactly the inputs the agent saw.
    agent_input_tool = StubSearchTool(results=search_results)
    agent_result = summarize(TOPIC, search_tool=agent_input_tool)
    agent_result_payload = agent_result.model_dump()

    judge_prompt = _build_judge_prompt(TOPIC, search_results_payload, agent_result_payload)

    client = anthropic.Anthropic()
    judge_response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=1024,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": judge_prompt}],
    )

    raw_judge_response = _extract_text(judge_response)
    verdicts, comments = _parse_judge_verdicts(raw_judge_response)
    pass_count = sum(1 for v in verdicts.values() if v == "pass")
    overall_score = f"{pass_count}/{len(verdicts)}"

    # ---- stdout report ----
    print("=" * 60)
    print(f"Topic: {TOPIC}")
    print(f"Agent model: {AGENT_MODEL}")
    print(f"Judge model: {JUDGE_MODEL}")
    print("=" * 60)
    print("\n-- Agent result --")
    print(json.dumps(agent_result_payload, indent=2))
    print("\n-- Judge prompt (truncated) --")
    print(judge_prompt[:600] + ("..." if len(judge_prompt) > 600 else ""))
    print("\n-- Judge verdicts --")
    for dim, verdict in verdicts.items():
        print(f"  {dim:<22} {verdict}")
    if comments:
        print(f"\n  comments: {comments}")
    print(f"\nOverall: {overall_score}")
    print("=" * 60)

    # ---- file trace ----
    trace = {
        "topic": TOPIC,
        "agent_model": AGENT_MODEL,
        "judge_model": JUDGE_MODEL,
        "search_results": search_results_payload,
        "agent_result": agent_result_payload,
        "judge_prompt": judge_prompt,
        "judge_verdicts": verdicts,
        "raw_judge_response": raw_judge_response,
        "overall_score": overall_score,
        "run_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    print(f"\nTrace written to: {OUTPUT_PATH.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()
