# Implementation Questions v2

**Date:** 2026-05-03
**Author:** Build agent
**Purpose:** Capture open questions encountered while executing the implementation plan. v1 questions are largely resolved or carry safe defaults; v2 captures only what arises during the actual build.

---

## Status of v1 Questions

| Q | Subject | Status |
|---|---|---|
| Q1 | `tavily-python` version to install | RESOLVED — `0.7.24` installed in `.venv`; will use as exact pin. |
| Q2 | Anthropic SDK / pinned model compatibility | DEFERRED — will surface in Phase 5 first real call. |
| Q3 | URL checker timeout + User-Agent | RESOLVED — using v5 defaults (5 s, `research-summarizer-link-check/1.0`). |
| Q4 | Workshop date for pin refresh | DEFERRED — recording today (2026-05-03) as pin date; README will flag refresh policy. |
| Q5 | `Creation_Questions_v5.md` other open items | RESOLVED — only Q3-equivalent items; v5 defaults applied. |
| Q6 | Level 2 skip guard scope | RESOLVED — using single guard requiring both keys (plan default). |
| Q7 | Committed `judge_eval_run.json` real or placeholder | RESOLVED — both keys confirmed present; will produce real trace. |

---

## Q1 (v2) — Sample-output topic substitution if URLs fail link-check

**Phase:** 13

**Question:** The plan's Phase 13 lists Wikipedia / NIH / NASA / DOE / DOI as preferred URL sources. If `scripts/check_sample_urls.py` returns non-200 for any URL on first run (Phase 13 escalation criterion), the plan says "replace the URL with a stable alternative; do not lower the script's pass threshold" — but does not say whether the same topic must be retained, or whether the topic itself can be swapped.

**Why it matters:** If a Wikipedia article moves or is split (rare but possible), the right replacement might be a different but equally stable URL on the same topic. If no such URL exists for the original topic, the topic itself must change, which has downstream effects on `evals/judge_eval.py` (which does not currently use these topics) but also on `exercises/level2_prompts.md` (which mentions "photosynthesis" by name).

**Suggested default if no answer:** Retain both topics (`photosynthesis`, `quantum_computing`) and substitute URLs only. If no stable substitute exists for a given topic, escalate via `notes/Escalations_Log.md` rather than swap the topic silently.

---

## Q2 (v2) — Whether to commit a regenerated `requirements-lock.txt` if `pip freeze` is noisy

**Phase:** 1

**Question:** `pip freeze` in the existing `.venv` will include packages installed transitively for tooling (e.g., setuptools, wheel) and possibly leftovers from prior experiments. Should `requirements-lock.txt` be the verbatim `pip freeze` output, or should it be filtered to the transitive closure of just the five top-level dependencies?

**Why it matters:** A noisy lock file is harder to read and may include packages that are not actually required to run the agent (slowing fresh-install onboarding by pulling in unnecessary deps).

**Suggested default if no answer:** Generate `requirements-lock.txt` from a fresh `pip install -r requirements.txt` run inside a clean virtualenv to capture only the true transitive closure. If a clean re-install is impractical, the verbatim `pip freeze` from the existing venv is acceptable as a less-clean fallback. (Plan's Phase 1.2 step 4 says `pip freeze > requirements-lock.txt` without specifying a fresh venv; the safer interpretation is that the build engineer is expected to start from a fresh venv but the existing one is close enough since it was created specifically for this project.)

---

## Q3 (v2) — Defective-agent behavior when forced to call `return_summary` with empty search results

**Phase:** 9

**Question:** With the empty-results guard removed (Phase 9 defect), the agent will pass an empty Search Results list to the LLM but still force a `return_summary` tool call via `tool_choice`. The model's behavior in this case is not deterministic at `temperature=1.0`:

- It may invent citations (Option B-style hallucination).
- It may return a `SummaryResult` with empty `key_findings` and `citations` lists.
- It may refuse the tool call (raising an error parseable as `pydantic.ValidationError` or producing a `tool_use` block with empty fields).

The defect-catching test (`test_no_results_raises_no_results_error`) asserts `pytest.raises(NoResultsError)`. Since no `NoResultsError` is raised, the test fails — but it fails *because* one of the above occurs. This means the **failure mode of the test** is not exception type per se but `Failed: DID NOT RAISE` from pytest.

**Why it matters:** This is fine for the workshop (the test still fails, which is the teaching point), but the verbatim pytest output captured in `solution/DEFECTS.md` may include an unrelated traceback (e.g., Pydantic validation error or Anthropic refusal) before the `Failed: DID NOT RAISE` line. The owner may want a cleaner failure mode.

**Suggested default if no answer:** Accept whatever pytest emits as the captured evidence. If the captured output is too noisy to be teaching-useful, escalate via `notes/Escalations_Log.md` and propose either (a) using a recording stub that short-circuits the LLM call, or (b) tightening the assertion to `pytest.raises((NoResultsError, anthropic.APIError, pydantic.ValidationError))` which would still fail because none of those is raised when the model invents content. Both options change the workshop's teaching emphasis, which is why this is a question rather than an autonomous decision.

---

## Q4 (v2) — Whether `tests/test_level2.py` should import `os` for the skip guard

**Phase:** 10

**Question:** The plan's Phase 10 says to "copy constants and skip guard from the solution file." The solution skip guard reads `os.environ.get("ANTHROPIC_API_KEY")`, requiring an `import os` at the top of the file. Imports are typically uncommented in test stubs, but `os` will be unused if the attendee doesn't fill in any tests that themselves use `os`. This produces no error but may surface a lint warning if attendees run a linter against their stubs.

**Why it matters:** Cosmetic only; does not affect pytest runs.

**Suggested default if no answer:** Include `import os` uncommented at the top of `tests/test_level2.py` since the skip guard depends on it and is itself uncommented. Lint warnings are an acceptable trade for a working skip guard.

---

## Q5 (v2) — Eval topic choice

**Phase:** 11

**Question:** The plan suggests "the discovery of penicillin" as the eval topic but does not lock it. If a different topic produces more reliable judge verdicts (i.e., less variance across runs at the judge's default temperature), should the topic be swapped?

**Why it matters:** The eval is meant to demonstrate a working judge run, not to stress-test the model. A topic that consistently passes all four rubric dimensions is the best demonstration material.

**Suggested default if no answer:** Use "the discovery of penicillin" as the plan suggests. If Phase 11 validation shows non-deterministic judge verdicts across two consecutive runs (cross-cutting rule #5), escalate rather than silently swap.
