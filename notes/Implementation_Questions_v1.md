# Implementation Questions v1

**Date:** 2026-05-03
**Purpose:** Open questions identified during initial environment and plan review.
**Status:** Unanswered — awaiting owner input before build begins.

---

## Q1 — `tavily-python` Version to Install

**Phase:** 1 (Scaffolding)

**Question:** `tavily-python` is not installed on this machine. The plan specifies `>=0.5,<1` as the version bounds. Should the build engineer install the latest version within that range, or is there a specific patch version that was validated during plan authoring?

**Why it matters:** If a specific version of `tavily-python` was used when designing the search tool interface in Phase 3, using a different patch version could cause surface-area differences (field names, error types) that would trigger a Phase 3 escalation.

**Suggested default if no answer:** Install the latest `>=0.5,<1` release and proceed. Escalate if the client API surface differs from `client.search(query=..., max_results=...)`.

---

## Q2 — Anthropic SDK Compatibility with Pinned Model

**Phase:** 5 (Agent Orchestration)

**Question:** The installed `anthropic` SDK is version 0.64.0. Is `claude-haiku-4-5-20251001` confirmed accessible with this SDK version and the API keys that will be provided to attendees?

**Why it matters:** The implementation plan explicitly forbids falling back to a model alias if the pinned model name fails (Phase 5 escalation, cross-cutting rule #1). If the model is not accessible, the build cannot proceed past Phase 5 without owner sign-off.

**Suggested default if no answer:** Proceed; the `verify_setup.py` script (Phase 14) will confirm model accessibility before workshop day. Escalate at Phase 5 if the model call fails.

---

## Q3 — `scripts/check_sample_urls.py` Timeout and User-Agent

**Phase:** 13 (Sample Outputs)

**Question:** The implementation plan notes two open items in `Creation_Questions_v5.md` for the URL checker script:

1. Per-request timeout: plan suggests 5 seconds as a safe default. Is this acceptable, or should it be a different value?
2. User-Agent header: plan suggests `research-summarizer-link-check/1.0` to avoid throttling by Wikipedia/academic publishers. Is this acceptable?

**Why it matters:** These are low-risk defaults but the plan explicitly flags them as open questions for owner confirmation.

**Suggested default if no answer:** Use the plan's suggested defaults (5-second timeout, `research-summarizer-link-check/1.0` User-Agent) and proceed.

---

## Q4 — Workshop Date for Pin Refresh

**Phase:** 1 (Scaffolding), 15 (README)

**Question:** The implementation plan requires recording a pin date in the README with a note to refresh if more than ~30 days old. What is the target workshop date? This determines whether the pins established during this build will need refreshing before the session.

**Why it matters:** If the workshop is more than 30 days from now, the README should flag that a pin-refresh pass is needed before workshop day. If it is less than 30 days away, the pins built today can be recorded as "current."

**Suggested default if no answer:** Record today's date (2026-05-03) as the pin date and note in the README that pins should be refreshed if the workshop is more than 30 days from the pin date.

---

## Q5 — `Creation_Questions_v5.md` Resolution Status

**Phase:** All

**Question:** The implementation plan's closing note states that two micro-tactical questions remain open in `Creation_Questions_v5.md` (the URL checker timeout and User-Agent, covered in Q3 above). Are there any other open items in `Creation_Questions_v5.md` that affect build decisions?

**Why it matters:** The plan is built on five rounds of Q&A. If any v5 questions beyond the two noted ones remain unresolved, they may surface as escalation triggers during build phases before the owner is available to answer them.

**Suggested default if no answer:** Proceed with the plan's documented safe defaults and escalate through `notes/Escalations_Log.md` if a build-blocking gap is discovered.

---

## Q6 — Level 2 Skip Guard: Both Keys or Anthropic Key Only?

**Phase:** 7 (Solution Tests), 10 (Attendee Stubs)

**Question:** The implementation plan's Phase 7.3 shows the Level 2 skip guard gating on *both* `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`. However, `test_result_fields_populated` injects a `StubSearchTool` directly — it does not need Tavily. Should the skip guard for `test_result_fields_populated` only require `ANTHROPIC_API_KEY`, while `test_photosynthesis_summary` (which calls the real search tool) requires both?

**Why it matters:** If the guard requires both keys for all Level 2 tests, an attendee with only an Anthropic key cannot run `test_result_fields_populated` even though it does not need Tavily. Splitting the guard could improve attendee experience but adds complexity to the stub file.

**Suggested default if no answer:** Use a single module-level guard requiring both keys (as shown in the plan) to keep the stub file simple and consistent.

---

## Q7 — Committed `judge_eval_run.json`: Real or Placeholder?

**Phase:** 11 (Evals), 13 (Sample Outputs)

**Question:** The plan requires committing a `sample_outputs/judge_eval_run.json` produced by running `evals/judge_eval.py` during Phase 11. This requires both API keys to be available and functional during the build. Confirming: the build engineer will have live API keys with sufficient quota to produce this trace artifact at build time?

**Why it matters:** Phase 11's escalation criteria call for first-failure escalation if `claude-sonnet-4-6` is unavailable at build time. If keys are not ready for Phase 11, the phase must halt rather than commit a placeholder.

**Suggested default if no answer:** Proceed assuming keys will be available. If Phase 11 is reached without functional keys, file an escalation entry in `notes/Escalations_Log.md` and halt.
