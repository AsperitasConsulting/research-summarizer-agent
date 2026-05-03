---
name: Creation Questions v4
description: Open items remaining after the v3 owner answers were folded into the plan; tactical refinements only — no scaffolding-blockers
type: project
---

# Creation Questions v4

The v3 round closed most of the structural decisions. The questions below are tactical — exact field names, exact exit-code semantics, and a template confirmation. None of them block scaffolding.

---

## Eval Trace Schema (Q5 v3 follow-up)

1. **Field name for the verbatim judge response.**
   The v4 plan adds a field to `sample_outputs/judge_eval_run.json` holding the raw assistant message text from the judge call. Candidate names:
   - **A.** `raw_judge_response` (plan default — descriptive, matches the verdicts field's `judge_` prefix)
   - **B.** `judge_response_text` (more explicit about the type)
   - **C.** `judge_message` (shorter; risks confusion with `judge_prompt`)
   - **Answer:** A.

2. **Should `raw_judge_response` capture the full Anthropic `Message` object structure (content blocks, stop reason, usage), or just the concatenated text from the `text` blocks?**
   - **A.** Full object — most fidelity, useful for instructor demos showing token usage too.
   - **B.** Concatenated text only — simpler, smaller file, easier for attendees to read by eye.
   - **Answer:** B.

---

## URL Check Script (Q11 v3 follow-up)

3. **HTTP method for `scripts/check_sample_urls.py`: HEAD or GET?**
   - **A.** HEAD — cheaper, but some sites (notably Wikipedia and a few CDN-fronted DOI hosts) return 405 to HEAD even though GET succeeds.
   - **B.** GET with response body discarded — universally compatible, slightly more bandwidth.
   - **Plan default:** B, for compatibility with the Wikipedia/NIH/NASA/DOI mix the owner confirmed in Q10 v3.
   - **Answer:** B.

4. **Should the script also verify `Content-Type: text/html` (or equivalent) to catch URLs that resolve but to a paywall/redirect page?**
   - Pro: catches more linkrot variants.
   - Con: increases false positives on legitimate redirects (e.g., NIH PMC PDF landing pages).
   - **Plan default:** No — only assert HTTP 200. Keep it simple.
   - **Answer:** No.

---

## Escalations Log Format (Q13 v3 follow-up)

5. **Confirm template for an `Escalations_Log.md` entry.**
   The plan proposes:

   ```markdown
   ## YYYY-MM-DD HH:MM UTC — Phase {N}: {one-line trigger}

   **Phase:** {phase number and name}
   **Trigger:** {which cross-cutting or per-phase criterion fired}
   **Attempts:** {what was tried, in order}
   **Observed result:** {what actually happened}
   **Hypothesis:** {best-guess root cause}
   **Halted at:** {the file/task the agent stopped on}

   ---
   ```

   - **A.** Confirmed as drafted.
   - **B.** Adjust fields: ___
   - **Answer:** A.

6. **Does an entry need to be appended to `Escalations_Log.md` even when the escalation is resolved without code change (e.g., owner says "ignore, proceed")?**
   - **A.** Yes — every escalation gets logged regardless of resolution.
   - **B.** No — only escalations that change scope or cause re-validation get logged.
   - **Plan default:** A — append-only, resolution-agnostic.
   - **Answer:** A.

---

## Resume-after-escalation Scope (Q14 v3 follow-up)

7. **"Re-validate the affected phase from the start" — what counts as "the affected phase"?**
   The plan numbers phases 1–15. Some phases are tightly scoped (Phase 6: package init); some are large (Phase 11: evals). For example, if an escalation hits during the *defect-reinsertion* step within Phase 9 but Phases 1–8 are clean, does "re-validate" mean:
   - **A.** Restart Phase 9 only (default — what the plan currently encodes).
   - **B.** Restart Phase 8 + Phase 9 together, since they share the validation-gate semantics.
   - **C.** Owner discretion at resume time — log entry asks the question explicitly.
   - **Plan default:** A.
   - **Answer:** A.

---

## Three-strike Rule Carveouts (Q12 v3 follow-up)

8. **Confirm carveouts to the three-strike rule.**
   The plan keeps a *first-failure* rule for the two validation gates (Phase 8 and Phase 9), since those phases exist precisely to surface deviation. Other candidate carveouts:
   - **A.** Confirmed: only Phase 8 and Phase 9 use first-failure escalation.
   - **B.** Add: secret-leak-risk triggers (cross-cutting #6) are also first-failure — never retry a redaction.
   - **C.** Adjust differently.
   - **Plan default:** B (Phase 8, Phase 9, and secret-leak-risk are all first-failure).
   - **Answer:** B.

---

## Solution Folder Warning Tone (Q1 v3 follow-up)

9. **Owner said "spoilers are not a concern."** The plan softens the v3 `solution/README.md` warning header from a do-not-peek banner to a one-line *"instructor reference"* note. Confirm tone:
   - **A.** Confirmed — one-line note, no boldface, no all-caps.
   - **B.** Remove `solution/README.md` entirely (the directory name speaks for itself).
   - **C.** Keep a lightly emphasized warning anyway.
   - **Plan default:** A.
   - **Answer:** A.
