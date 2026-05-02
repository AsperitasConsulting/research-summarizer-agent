# Creation Thinking v3

**Inputs reviewed:**
- `requirements/Research_Summarizer_Agent_Spec.md` (v1.0 draft)
- `requirements/Testing-Pyramid.md`
- `notes/Creation_Thinking_v1.md` and `notes/Creation_Thinking_v2.md`
- `notes/Creation_Questions_v1.md` and `notes/Creation_Questions_v2.md` (both with project-owner answers inline)
- `plans/ImplementationPlan.md` (v2)

This document captures three things: how the v2 question answers refine the v2 plan, the two structural additions the project owner has now requested (solution-first validation and per-phase human escalation criteria), and the residual risk that those changes introduce. Open items live separately in `Creation_Questions_v3.md`.

---

## What Actually Changed Since v2

### Owner Answers in `Creation_Questions_v2.md`

| # | Topic | v2 Position | v3 Direction |
|---|-------|-------------|--------------|
| 1 | Tavily key sourcing | Open | Pre-supplied — workshop hands keys to attendees |
| 2 | Anthropic key sourcing | Open | Pre-supplied — same as above |
| 3 | Network constraints | Open | Conference provides unrestricted wifi; not a concern |
| 4 | Defect "obvious by omission" | No marker | **Place a comment marker at the gap** |
| 5 | Single defect or layered | Open | One defect — simplicity beats optionality |
| 6 | Sample URL realism | Open | **Real but common, unlikely to change** (was synthetic `example.com` in v2) |
| 7 | Sample count | Open | Two is sufficient |
| 8 | Judge model | Sonnet recommended | Confirmed — `claude-sonnet-4-6` |
| 9 | Rubric scheme | Pass/fail recommended | Confirmed |
| 10 | Eval failure-topic strategy | Open | No preference — owner needs the agent to experiment |
| 11 | Trace artifact | Open | **Write eval output to file** under `sample_outputs/` for instructor reference |
| 12 | Level 2 prompts file | Level 1 only | **Add parallel prompts for all levels** (Level 1 + Level 2) |
| 13 | Prompt phrasing voice | Imperative | **Conversational** — models good agent-collaboration habits |
| 14 | README walkthrough | Open | Stay narrow — setup and run only |
| 15 | Pin-refresh playbook | Open | Include 30-second copy-paste commands |
| 16 | Tavily reachability check | Open | Trust the key, do not call |
| 17 | `verify_setup.py` verbosity | Open | **Diagnostic detail** (Python version, SDK versions, etc.) |
| 18 | `requirements-lock.txt` | Open | **Generate it** alongside `requirements.txt` |
| 19 | Repo directory rename | Open | Leave as `research-summarizer-agent/` |
| 20 | Branding/attribution | Open | None |

### Two Structural Changes the Owner Now Requires

These are the substantive revisions, not just refinements:

1. **Solution-first validation sequence.** After the agent is constructed, the build team must write the *complete* solution tests, run them, and confirm they behave as expected — *before* converting them into the commented stub files attendees see. The intent is to catch any agent/test misalignment *during the build* rather than during the workshop. This shifts the build from "ship a defective agent and hope the stubs are catchable" to "prove the stubs are catchable, then ship."

2. **Human escalation criteria on every phase.** The agent team is to escalate to a human when it gets stuck. Each phase needs concrete escalation triggers — the conditions under which the team must stop autonomous work and ask. This protects against silent drift, hidden assumption-stacking, and the model-nondeterminism failure modes that an agent team cannot reliably detect on its own.

---

## Why Solution-First Validation Helps

The v2 plan ships the agent with a seeded defect (Option A — no `NoResultsError` on empty results). The Level 1 stub `test_no_results_raises_no_results_error` is supposed to fail when an attendee fills it in, surfacing the defect. The hidden risk in v2 is that *we are trusting the spec's claim* that this test catches this defect. We have not actually run a working version of the test against the defective agent to confirm.

The new sequence makes that proof a build artifact:

1. Build the agent **with the defect omitted** (i.e., the correct version).
2. Write the full solution tests.
3. Run them. They must all pass. If any do not, the agent or the test is wrong — escalate.
4. Insert the defect into the agent.
5. Re-run the solution tests. Exactly the defect-catching test (and no other) must now fail. If more or fewer tests fail than expected, the defect's blast radius does not match what the workshop expects to teach — escalate.
6. Restore the defective agent as the shipped state, and convert the verified solutions into commented stubs.

The cost of this sequence is one extra Level 2 API run (small) and a strict gate before stub conversion. The benefit is that the workshop ships with empirical evidence the seeded defect is catchable in the way the design promises.

### Where Do the Solutions Live?

This is the new wrinkle. The v1 Q4 answer said "omit the solution for now — owner builds it later." The new validation sequence forces us to write the solutions during this build. Three options:

- **A. Keep them committed to main under `solution/`,** clearly marked as instructor-only (`solution/README.md` warns attendees not to peek). Pros: validation re-runnable, owner has a reference, no work thrown away. Cons: contradicts the v1 answer's spirit; attendees can see them in the repo.
- **B. Commit them to a `solution` branch only.** Pros: matches the v1 Q4 spirit; clean main branch. Cons: branch-juggling complicates the build sequence and the validation re-run.
- **C. Write them, validate, then delete before final commit.** Pros: cleanest main branch. Cons: throws away tested artifacts the owner was going to build later anyway; future revalidation has to start from scratch.

**Plan default: Option A**, with a stark `solution/README.md` and a top-of-file warning header in every solution test. The owner can downgrade to B or C in review. This question is also raised in `Creation_Questions_v3.md`.

---

## Why Per-Phase Escalation Criteria

Agent teams have two failure modes humans usually catch:

- **Stuck loops** — re-attempting the same fix with cosmetic variations rather than recognizing the problem is structural.
- **Silent drift** — adding scope, abstraction, or workarounds the spec did not authorize, often because a small obstacle felt easier to route around than to flag.

Both are mitigated by having the team commit, *in advance*, to triggers that demand a human in the loop. The triggers in this plan share a few patterns:

- **Two-strike rule.** If a discrete attempt fails twice with no new diagnostic information, escalate. (Two is enough to rule out flakes; three crosses into wasted compute.)
- **Spec contradictions.** Any moment where the spec, the v1 answers, the v2 answers, or this plan disagree — stop and ask. Do not pick a winner.
- **External-dependency surprises.** Anthropic SDK behavior, Tavily behavior, or Pydantic/Anthropic schema-rejection issues that aren't documented in either the spec or this plan are out-of-band — escalate before working around them.
- **Model-nondeterminism rule.** Any Level 2 or eval result that varies meaningfully across two consecutive runs at `temperature=0` is a signal the test is too tight or the prompt is unstable — escalate, do not loosen the assertion silently.

Per-phase triggers in the plan layer onto these.

---

## Reassessed Architecture Snapshot

```
research-summarizer-agent/
├── agent/                      (unchanged from v2)
├── solution/                   (NEW — instructor-only; see Q1 in v3 questions)
│   ├── README.md               (do-not-peek warning)
│   ├── tests/
│   │   ├── test_level1.py      (full solutions)
│   │   └── test_level2.py      (full solutions)
│   └── DEFECTS.md              (which defect, why, fix diff)
├── tests/
│   ├── __init__.py
│   ├── test_level1.py          (commented stubs derived from solution/)
│   └── test_level2.py          (commented stub derived from solution/)
├── evals/
│   └── judge_eval.py
├── exercises/
│   ├── level1_prompts.md
│   └── level2_prompts.md       (NEW per Q12 v2)
├── sample_outputs/
│   ├── photosynthesis.json
│   ├── quantum_computing.json
│   └── judge_eval_run.json     (NEW per Q11 v2 — eval trace artifact)
├── verify_setup.py
├── .env.example
├── requirements.txt
├── requirements-lock.txt       (NEW per Q18 v2)
└── README.md
```

`DEFECTS.md` re-enters scope because it is part of the solution suite the owner originally planned to build later — this build now produces it as part of validation. If the owner chooses Option C above (delete solutions after validation), `DEFECTS.md` would also be deleted; that decision is in v3 questions.

---

## Risks Added by the v3 Changes

1. **Solutions in main branch make spoilers visible.** Mitigation: `solution/` README and per-file warning headers, plus an explicit check in `verify_setup.py` (or README troubleshooting) that attendees know `solution/` exists and should be skipped. Open question: should `solution/` be moved out of main entirely?

2. **Validation Level 2 burns a real API call during build.** Cost is trivial in absolute terms but the build now requires `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` to be present at build time. Document this in the plan's prerequisites.

3. **Defect insertion-and-removal cycle introduces a window where the agent is in an inconsistent state.** Mitigation: the build sequence does insertion *after* the solutions are validated against the correct agent, so the failing-test-must-be-defect check becomes a one-shot gate. Use a clearly named helper or a documented diff so the operator (or future reviewer) can replay.

4. **The "place a comment marker at the gap" answer (Q4 v2) makes the defect more visible than v2 assumed.** This may reduce the discovery satisfaction the v2 plan optimized for, but it serves the mixed-skill-audience goal better. Wording for the marker comment is in v3 questions — getting it wrong could either spoil the answer or fail to signal the gap.

5. **Real (not synthetic) URLs in `sample_outputs/` reintroduce the linkrot risk** that v2 explicitly avoided. The owner accepted this in Q6 v2 by scoping to "common and unlikely to change" URLs. We need a stable-pick rule (e.g., Wikipedia, NIH, well-known encyclopedia entries) and a manual link-check step before workshop date.

6. **Per-phase escalation criteria can become a paperwork ritual** if they are too granular or too generic. The plan tries to keep them concrete and actionable per phase, but reviewers should call this out if any criterion reads like boilerplate.

---

## What Remains Open

Captured in `notes/Creation_Questions_v3.md`. The two largest are: (1) where the validated `solution/` directory lives in the long run, and (2) what wording the defect-marker comment should use. Both are small in scope but affect attendee experience directly.
