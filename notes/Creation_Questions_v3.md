# Creation Questions v3

Open items remaining after incorporating the v1 and v2 answers and adding the new solution-first validation sequence and per-phase human escalation criteria. None of these block scaffolding — they refine the build's outputs and the operator's decision rules.

---

## Solution Directory Placement

1. **Where do the validated solutions live in the long run?**
   The v1 Q4 answer was "omit the solution for now — owner builds it later via Claude Code." The new instruction in this turn requires the solutions to be written and verified during this build. The v3 plan defaults to keeping `solution/` in the main branch with an instructor-only `README.md` warning attendees off. Three alternatives:
   - **A. Keep in main (plan default)** — clearest validation re-run path; spoiler risk to attendees who poke around.
   - **B. Move to a `solution` branch** — matches the v1 Q4 spirit; complicates re-validation and the build sequence.
   - **C. Delete after stub conversion** — cleanest main; validation becomes one-shot and re-validation later requires regenerating the solutions.
   - **Answer:**

2. **Should `solution/DEFECTS.md` ship in main alongside the solutions, regardless of which option above is chosen?**
   It is small, instructor-only, and useful as a build artifact even if the solutions themselves are deleted (Option C above).
   - **Answer:**

---

## Defect Comment Marker

3. **Exact wording of the marker comment at the defect gap.**
   The v3 plan uses `# (handle empty results before prompting)` as a placeholder per Q4 v2. Alternatives:
   - **A.** `# (handle empty results before prompting)` (plan default — neutral, descriptive)
   - **B.** `# (search results returned)` (the v2 thinking-doc fallback — quieter, more invitation-to-think)
   - **C.** `# TODO: handle empty results` (most explicit; arguably too on-the-nose for the discovery moment)
   - **D.** Other wording the owner prefers.
   - **Answer:**

4. **Should the marker comment ALSO appear in `tests/test_level1.py` (in the commented stub for `test_no_results_raises_no_results_error`) as a pointer to where to look in the agent code?**
   Pro: helps slower attendees connect the dots. Con: dilutes the "find it yourself" moment that gives Level 1 its punch.
   - **Answer:**

---

## Eval Trace Artifact

5. **`sample_outputs/judge_eval_run.json` schema confirmation.**
   The v3 plan defines a specific JSON schema (topic, models, search_results, agent_result, judge_prompt, judge_verdicts, overall_score, run_at). Should the file include the full **judge response text** (raw, not just parsed verdicts) so an instructor can show "what the judge actually said" during Segment 5?
   - **Answer:**

6. **Overwrite vs. timestamped filename.**
   Re-running `judge_eval.py` overwrites `judge_eval_run.json` in the v3 plan. Alternative: write `sample_outputs/judge_eval_run_<ISO-8601>.json` so each run is preserved. Overwrite is simpler; timestamping helps if an instructor wants to compare runs in real time.
   - **Answer:**

7. **Should `judge_eval_run.json` be committed to the repo as a "known-good example run," or always be a build/runtime artifact added to `.gitignore`?**
   Committing it gives attendees a reference even if they cannot run the eval themselves. Gitignoring it keeps the repo tidy and avoids stale artifacts.
   - **Answer:**

---

## Solution Test Decisions

8. **`test_result_fields_populated` placement.**
   The v3 plan keeps this as a Level 1 test even though it calls the real Anthropic API (the search side is stubbed but the LLM side is not). The plan offers a structural alternative (recording stub asserting `search()` was called once). Confirm Level 1 placement with a real API call, or move to Level 2, or use the structural alternative?
   - **Answer:**

9. **Solution Phase 9 nondeterminism floor.**
   The plan asserts the defective agent must produce a "consistent symptom" — i.e., the LLM-with-no-search-results call must reliably fail the assertion in `test_no_results_raises_no_results_error` (which it will, because the test asserts on `NoResultsError` being raised, not on LLM behavior). But edge case: what if the LLM-call step itself raises an `anthropic.APIError` because the empty-prompt is malformed enough to fail server-side validation? The test would still fail (on a different error class) — should the assertion in `test_no_results_raises_no_results_error` be tightened to expect specifically `NoResultsError` (current plan) or broadened to expect "any failure"?
   - **Answer:**

---

## Sample Output URL Stability

10. **Preferred sources for "real but stable" URLs.**
    The v3 plan suggests Wikipedia, NIH/NCBI, NASA/DOE, and open-access DOIs as the candidate pool. Confirm this list, or specify additional/excluded sources?
    - **Answer:**

11. **Pre-workshop URL refresh cadence.**
    The plan adds a one-line note in the README that someone should curl each citation URL before the workshop date. Should the build also include a tiny `scripts/check_sample_urls.py` (or shell script) that does this check programmatically? Pro: turns the manual step into one command. Con: another file to maintain.
    - **Answer:**

---

## Escalation Mechanics

12. **Two-strike rule scope.**
    The cross-cutting protocol uses "two failed attempts on the same task" as the escalation trigger. Is two the right threshold, or should it be one (escalate immediately on first failure for high-risk tasks like the Phase 9 defect-validation gate) or three (give the team more room on low-stakes tasks)?
    - **Answer:**

13. **Escalation channel.**
    The plan says the team "surfaces to a human" on escalation but does not specify the channel. Options: a comment in the working file, a note in `notes/Escalations_Log.md`, an explicit pause in the build with a printed message, or something else. What does the owner expect?
    - **Answer:**

14. **Resume-after-escalation behavior.**
    Once a human responds to an escalation, should the team:
    - **A.** Resume the exact in-progress task with the human's guidance applied.
    - **B.** Re-validate everything from the start of the affected phase.
    - **C.** Decide case-by-case based on the escalation's nature.
    - **Answer:**

---

## Build Prerequisites

15. **Build-time API key availability.**
    Phase 8 (validate solutions) and Phase 9 (re-validate after defect insertion) require both `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` during the build. Will those keys be supplied to the build environment, or should the plan include a "skip Level 2 validation, mark as pending" fallback for builds without keys?
    - **Answer:**

16. **Solution authoring agent vs. human.**
    The new solution-authoring step (Phase 7) was originally planned as a "owner builds later via Claude Code" exercise. This build has the agent team write the solutions instead. Is the owner still planning to redo this step in their own dry-run, or do the validated solutions in this build replace that exercise entirely?
    - **Answer:**
