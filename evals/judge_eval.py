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

from dotenv import load_dotenv


_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from agent import StubSearchTool, summarize  # noqa: E402
from agent.tools import TavilySearchTool  # noqa: E402
from evals.judge import (  # noqa: E402
    JUDGE_MODEL,
    build_judge_prompt,
    run_judge,
)


load_dotenv()


# Pinned models. Do not swap to aliases — the workshop teaches model pinning.
AGENT_MODEL = "claude-haiku-4-5-20251001"
TOPIC = "the discovery of penicillin"

OUTPUT_PATH = _REPO_ROOT / "sample_outputs" / "judge_eval_run.json"


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

    judge_prompt = build_judge_prompt(TOPIC, search_results_payload, agent_result_payload)
    verdicts, comments, raw_judge_response = run_judge(
        TOPIC, search_results_payload, agent_result_payload
    )
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
