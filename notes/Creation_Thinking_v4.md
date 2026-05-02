---
name: Creation Thinking v4
description: v4 reasoning — incorporates owner answers in Creation_Questions_v3.md and folds them into the implementation plan
type: project
---

# Creation Thinking v4

**Inputs reviewed:**
- `requirements/Research_Summarizer_Agent_Spec.md` (v1.0 draft)
- `requirements/Testing-Pyramid.md`
- `notes/Creation_Thinking_v1.md`, `Creation_Thinking_v2.md`, `Creation_Thinking_v3.md`
- `notes/Creation_Questions_v1.md`, `Creation_Questions_v2.md`, `Creation_Questions_v3.md` (all with owner answers inline)
- `plans/ImplementationPlan.md` (v3.0)

This document captures (1) how each v3 answer changes the v3 plan, (2) the secondary effects those answers create, and (3) the residual risks worth flagging. New open items live in `Creation_Questions_v4.md`.

---

## What Changed Since v3

### Owner Answers in `Creation_Questions_v3.md`

| # | Topic | v3 Plan Default | v4 Direction |
|---|-------|-----------------|--------------|
| 1 | `solution/` directory placement | Option A (kept in main, instructor-only with warning) | **Option A confirmed** — *"spoilers are not a concern."* The aggressive warning header softens; `solution/README.md` becomes a one-liner noting "instructor reference," not a do-not-peek banner. |
| 2 | `solution/DEFECTS.md` ships alongside solutions | Yes | **Confirmed** |
| 3 | Defect marker comment wording | Option A (`# (handle empty results before prompting)`) | **Option C — `# TODO: handle empty results`**. Most explicit; the workshop accepts the discovery moment being on-the-nose. |
| 4 | Marker comment also in `tests/test_level1.py` stub | Open | **Yes** — pointer comment in the commented stub for `test_no_results_raises_no_results_error` directing attendees to look near the matching marker in `agent/agent.py`. Speeds slower attendees through the connection. |
| 5 | `judge_eval_run.json` includes raw judge response text | Open | **Yes** — store both the parsed verdicts and the verbatim judge output so an instructor can show "what the judge actually said" during Segment 5. |
| 6 | Overwrite vs. timestamped trace filename | Overwrite | **Confirmed** |
| 7 | Commit `judge_eval_run.json` to repo | Open | **Commit it** as a known-good example run. Attendees who can't run the eval still see the reference output. |
| 8 | `test_result_fields_populated` placement | Level 1 (with caveat) | **Move to Level 2.** It calls real Anthropic, so its natural home is the constrained-model tier. This makes Level 1 fully deterministic (no API calls) and shrinks the Level 1 stub count. |
| 9 | Tighten `NoResultsError` assertion | Tighten | **Confirmed** |
| 10 | Stable URL source list | Wikipedia / NIH / NASA / DOE / OA DOIs | **Confirmed** |
| 11 | Scripted URL check before workshop | Open | **Add `scripts/check_sample_urls.py`** — a tiny script that curl-pings each citation URL in `sample_outputs/` and reports 200/non-200 with elapsed time. Turns the manual pre-workshop check into one command. |
| 12 | Two-strike rule threshold | Two failed attempts | **Three failed attempts.** Adds slack on low-stakes work. The high-stakes gates (Phase 8 / Phase 9) keep their first-failure escalation rule because the gate exists *to* surface mismatch. |
| 13 | Escalation channel | Open | **Produce `notes/Escalations_Log.md` AND stop work.** The log is the artifact; the hard stop is the load-bearing behavior. The agent does not auto-resume. |
| 14 | Resume-after-escalation behavior | Open | **Option B — re-validate everything from the start of the affected phase.** Prevents an in-flight inconsistency from leaking past the human's response. Slightly more work, but the safer default given the validation-gate pattern. |
| 15 | Build-time API keys available | Yes | **Confirmed** — both `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` will be present during Phase 8 / Phase 9 validation runs. |
| 16 | Solutions vs. attendee live-coding | Owner builds later | **Solutions are this build's deliverable.** Attendees rewrite the equivalents in `tests/` during the workshop; the validated `solution/tests/` directory is instructor-side reference. The `tests/` directory ships with commented stubs for that rewriting work. |

---

## Secondary Effects of the v3 Answers

### Effect of Q3 + Q4 (defect marker wording and stub pointer)

The combined effect of using the most explicit marker (`# TODO: handle empty results`) **and** including a pointer in the test stub is that the defect crosses the line from "discovery-by-attendee" into "discovery-with-guidance." That is the owner's intent — the workshop has a mixed-skill audience and the punchline value is preserved by the assertion-writing exercise, not by the find-the-gap exercise.

Practical consequence: the defect is now extremely findable. The teaching moment relocates from "can you spot orchestration logic that's missing?" to "can you write a deterministic test that fails fast against a known orchestration bug?" That is fully compatible with the testing-pyramid teaching goal.

### Effect of Q8 (move `test_result_fields_populated` to Level 2)

This rebalances the test count:

- **Level 1 (deterministic, no API):** 1 passing example + 2 commented stubs = 3 tests total
  - `test_empty_topic_raises_value_error` (passing)
  - `test_no_results_raises_no_results_error` (stubbed; defect-catching)
  - `test_search_tool_error_propagates` (stubbed)
- **Level 2 (constrained-model, real API):** 1 passing-style example + 1 commented stub = 2 tests total
  - `test_photosynthesis_summary` (the original Level 2 stub — keeps its skip guard)
  - `test_result_fields_populated` (relocated from Level 1; now also gated by the API-key skip marker)

Workshop-clock impact: the 30–45 min coding budget gets easier to hit because Level 1 is now smaller and entirely offline. The Level 2 work expands modestly — but Level 2 was always optional/aspirational for slower attendees, so the cost lands where there is slack.

### Effect of Q5 + Q7 (raw judge text + committed trace)

`sample_outputs/judge_eval_run.json` is now a versioned artifact. Two implications:

- **Schema needs a `raw_judge_response` field** (or similar) holding the verbatim assistant message text from the judge call. It coexists with the parsed `judge_verdicts` map.
- **The committed snapshot can drift.** Re-running the eval after a model bump or prompt change will produce a different file. The plan should note that whoever bumps a pin or edits the eval script must re-run and re-commit, or the example diverges from reality. This is mild — it's a known cost of committing run artifacts.

### Effect of Q11 (`scripts/check_sample_urls.py`)

Adds a `scripts/` directory at the repo root. The script is tiny — one HTTP HEAD per URL, a print line per result, exit code 0 if all 200, 1 otherwise. It is not part of `verify_setup.py` because its concern is workshop-prep, not attendee-prep. The README's pre-workshop section (currently a sentence) becomes a one-line shell invocation.

### Effect of Q12–Q14 (escalation mechanics)

Three connected changes:

- **Three-strike rule for ordinary tasks; first-failure rule for validation gates.** The gates (Phases 8 and 9) are designed *to detect* deviation; their failure is signal, not flake.
- **`notes/Escalations_Log.md` is the persistent artifact.** Format: append-only entries with phase, trigger, attempt summary, observed result, hypothesized cause. The log is for the human who responds; it also serves as a build retrospective.
- **Resume strategy B (re-validate the affected phase from the start) is the default.** Re-running a phase from the start trades compute for confidence. For Phase 8 / Phase 9, that means re-running all solution tests after the human's resolution — which is precisely what the owner would want to verify the fix.

The combined behavior: the agent runs autonomously up to a strike-three or gate-failure, writes a log entry, halts. After the human resolves, the agent restarts the affected phase from its first task. No partial-state surprises.

---

## Reassessed Architecture Snapshot

```
research-summarizer-agent/
├── agent/                          (unchanged from v3)
├── solution/                       (instructor reference; warning softened)
│   ├── README.md                   (one-line "instructor reference" header)
│   ├── DEFECTS.md
│   └── tests/
│       ├── __init__.py
│       ├── test_level1.py          (3 tests; deterministic)
│       └── test_level2.py          (2 tests; gated on API keys)
├── tests/
│   ├── __init__.py
│   ├── test_level1.py              (1 passing + 2 commented stubs; one stub
│   │                                includes the marker pointer per Q4)
│   └── test_level2.py              (2 commented stubs)
├── evals/
│   └── judge_eval.py
├── exercises/
│   ├── level1_prompts.md           (4–6 prompts, mapped to the 3 Level 1 tests)
│   └── level2_prompts.md           (1–2 prompts, mapped to the 2 Level 2 tests)
├── sample_outputs/
│   ├── photosynthesis.json
│   ├── quantum_computing.json
│   └── judge_eval_run.json         (committed; includes raw judge text)
├── scripts/
│   └── check_sample_urls.py        (NEW per Q11 v3)
├── notes/
│   └── Escalations_Log.md          (NEW per Q13 v3 — created on first escalation;
│                                    template documented in the plan; absent if no
│                                    escalations occurred)
├── verify_setup.py
├── .env.example
├── requirements.txt
├── requirements-lock.txt
└── README.md
```

`Escalations_Log.md` is created on demand. If the build runs cleanly, the file is never written. The plan documents its template so any agent that needs to write it knows the shape without re-asking.

---

## Risks Added or Reshaped by v4

1. **The defect is now very visible.** `# TODO: handle empty results` plus a pointer in the test stub is two flashing signs. Risk: stronger attendees feel patronized; workshop loses some "aha" voltage. Mitigation: positioning in the workshop script — frame Level 1 as "writing a test for a known bug," not "find the bug." The owner has accepted this trade.

2. **Committed `judge_eval_run.json` will go stale.** Mitigation: README pin-refresh playbook now also says "if you re-run the eval, commit the new trace." A small process discipline; less risky than not committing it at all.

3. **`scripts/check_sample_urls.py` is one more file to maintain.** Mitigation: keep it under 40 lines, no dependencies beyond `urllib`/`requests` (already in transitive closure), and exit-code-driven so CI or a pre-workshop check can call it.

4. **Three-strike rule increases compute cost on stuck loops.** Mitigation: the cross-cutting protocol still requires *new diagnostic information between attempts*. A repeat of the same failure with no new diagnostic still triggers an immediate escalation regardless of strike count.

5. **`Escalations_Log.md` could become a task list rather than an alert mechanism.** Mitigation: plan specifies *append-only* and that the log entry alone is not a resolution — the agent halts, no resumption is implicit.

6. **Move of `test_result_fields_populated` to Level 2 increases the API-key dependency surface for the Level 2 stub set.** Mitigation: skip-marker is already on the file (Phase 7 v3 spec); both Level 2 tests share the same gate; no new dependency.

---

## What Remains Open

Captured in `notes/Creation_Questions_v4.md`. The set is small — most of the v3 answers were locked. Remaining items are tactical: exact field names in the eval JSON schema, exit-code semantics for the URL-check script, and the precise template for the escalations log entry.
