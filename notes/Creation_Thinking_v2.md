# Creation Thinking v2

**Inputs reviewed:**
- `requirements/Research_Summarizer_Agent_Spec.md` (v1.0 draft)
- `requirements/Testing-Pyramid.md`
- `notes/Creation_Thinking_v1.md` (prior analysis)
- `notes/Creation_Questions_v1.md` (with inline answers from project owner)
- `plans/ImplementationPlan.md` (v1)

This document captures how the answers in `Creation_Questions_v1.md` change the plan, the new design decisions that flow from them, and the remaining risks. New open questions are tracked separately in `Creation_Questions_v2.md`.

---

## How the Answers Shape v2

The answers tighten almost every previously-open decision. The plan moves from "build team chooses" toward concrete version pins, concrete file counts, and concrete scope boundaries. The most consequential answers:

| # | Topic | v1 Position | v2 Direction |
|---|-------|-------------|--------------|
| 1 | Pytest comments | Light | **Extensive** — starter files teach pytest, not just the agent |
| 2 | Workshop length | Unspecified | **90 min total, 30–45 min coding** — sets test stub budget |
| 3 | Tavily key | Open | **Required for attendees** (they bring their own free-tier key) |
| 4 | Solution branch | Folder vs branch | **No solution shipped** — owner builds it later as a workshop dry-run |
| 5 | Anthropic SDK | Unpinned | **Latest stable at build time**, may re-pin closer to June |
| 6 | Python ceiling | None | **Set a ceiling** to avoid bleeding-edge surprises |
| 7 | Pydantic | v2 recommended | **v2 pinned** |
| 8 | Structured output | Open | **Native Anthropic tool_use** — no `instructor` dependency |
| 9 | Sample outputs | Unspecified | **JSON, 2–3 topics** |
| 10 | Level 1 prompts | Ambiguous | **Prompts attendees give to Claude Code**, not prompts for the agent |
| 11 | Eval audience | "Demo" | **Instructor-run, attendee-runnable after** — must be polished but documented |
| 12 | Defect visibility | Open | **Obvious** — assume mixed skill levels |
| 13 | DEFECTS.md | Choice + ? | **Include the fix** — full reference for the instructor |

---

## Workshop Time Budget Drives Scope

90 minutes, 30–45 minutes of coding, is the single most useful constraint we now have. Working backward:

- **Segment 1 (Setup, ~10 min):** `verify_setup.py` runs clean.
- **Segment 2 (Concept intro, ~15 min):** Walk through the agent code and the testing pyramid.
- **Segment 3 (Level 1 tests, ~25 min):** Attendees write deterministic tests with `StubSearchTool`.
- **Segment 4 (Level 2 tests, ~15 min):** Attendees add a constrained-model test.
- **Segment 5 (LLM-as-judge demo, ~15 min):** Instructor runs `judge_eval.py`, attendees observe.
- **Buffer (~10 min):** Q&A, cleanup.

That gives roughly:
- **Level 1 starter file:** 1 passing test + 3–4 commented stubs. More than that, slow attendees feel underwater.
- **Level 2 starter file:** 1 stub test. The cost of a real API call per iteration dominates; one well-designed assertion is enough to teach the pattern.
- **Level 1 prompts file:** 4–6 carefully worded prompts, mapping 1:1 to the stubs. Each prompt nudges toward a specific test without revealing the assertion.

Writing more stubs would seem helpful, but for a 30–45 minute coding window it would make the experience feel like a checklist instead of a learning moment.

---

## Concrete Decisions Made for v2

### Pydantic v2 + Anthropic Native Tool Use

The structured-output mechanism is the single most fragile integration point. With native tool use:

1. Convert the `SummaryResult` Pydantic model to a JSON schema via `model_json_schema()`.
2. Pass that schema as a single tool to `client.messages.create(...)`.
3. Force the model to use it via `tool_choice={"type": "tool", "name": "return_summary"}`.
4. Parse the resulting `tool_use` block's `input` dict back through `SummaryResult.model_validate(...)`.

This is the simplest path that:
- Avoids a third-party schema library (`instructor`, `outlines`, etc.)
- Gives Pydantic v2 a chance to surface a validation error if the model drifts
- Keeps the agent code under ~60 lines

### Version Pins

Specific pins must be captured at build time by running `pip install` against current PyPI and committing the resolved versions. The plan will show **placeholder upper/lower bounds** plus the build instruction to lock with `pip freeze`. Today (2026-04-30):

- `python_requires = ">=3.11,<3.14"` — keeps 3.11/3.12/3.13 in scope, avoids the still-young 3.14 line.
- `anthropic` — pin to whatever is latest stable when scaffolding runs; document the date.
- `pydantic >= 2.7, < 3` — v2 broadly stable; the exact minor pinned at build time.
- `tavily-python >= 0.5, < 1` — same approach.
- `pytest >= 8, < 9`.
- `python-dotenv >= 1, < 2`.

The README and `requirements.txt` should both note "Pinned on YYYY-MM-DD; refresh before the workshop date if more than ~30 days old."

### Defect Implementation Style

"Obvious" defect, mixed skill levels in the room — the right shape is a missing block of code, **not** a buggy block of code. Specifically: omit the empty-results check entirely between `search_tool.search(...)` and prompt building. No comment, no TODO. A reader who knows about `NoResultsError` (it's defined in `tools.py` and listed in the README's Exceptions table) will spot the gap. A reader who doesn't know about it will only see the gap once a Level 1 test fails — which is exactly the intended teaching moment.

The fix on the solution branch is a 2-line guard:
```python
if not results:
    raise NoResultsError(topic)
```

### Solution Branch Strategy

Per the answer to Q4: **do not produce a solution branch as part of this build**. The project owner will create it later by running through the workshop using Claude Code, which lets them validate the same attendee experience. This means:

- `solution/` directory: **delete from the layout** (the v1 plan still listed it).
- `DEFECTS.md`: still document it in the plan (so the owner knows what to write later), but do not create the file in this build.
- Implementation plan should explicitly mark "produced later by the owner" as the path for these artifacts.

### Starter File Pedagogy

Because attendees may be new to pytest, the starter files need:

- A **header docstring** in each test file explaining what fixtures/parametrize/etc. mean.
- **Inline comments** on every fixture and the one passing test, narrating what's happening.
- **Commented stubs that read as instructions**, not just function shells. Example:

  ```python
  # def test_no_results_raises_no_results_error(stub_results):
  #     # Arrange: build a StubSearchTool with an empty results list
  #     # Act: call summarize() and capture what it does
  #     # Assert: pytest.raises(NoResultsError) wraps the call
  #     pass
  ```

This shoulders the pytest-conventions burden so attendees can focus on the testing-pyramid concepts.

### Sample Outputs

JSON files are easier to read than serialized Python and don't tempt attendees into copy-pasting. Two topics is sufficient; "photosynthesis" (simple, factual) and "quantum computing" (technical, multiple perspectives) cover the variety the workshop needs. A third (e.g., "espresso brewing") is optional if the build engineer has bandwidth.

### Eval Polish Level

Per the answer to Q11, the LLM-as-judge eval is instructor-run **but** attendee-runnable. That sets the polish bar:

- Idempotent (no caches, no flags expected to be pre-set).
- Clear print output a workshop screen can show without surgery.
- Comments explaining the rubric design — so attendees who run it later can read the prompt and learn from it.
- Uses a different model than the agent (Sonnet) so the demo also illustrates the judge-vs-actor separation.

---

## Updated Architecture Snapshot

Files and approximate sizes the v2 plan will produce:

```
research-summarizer/
├── agent/
│   ├── __init__.py        (~5 lines)
│   ├── agent.py           (~60 lines)  - pipeline + summarize()
│   ├── tools.py           (~80 lines)  - SearchTool protocol + impls + errors
│   ├── models.py          (~25 lines)  - Pydantic v2 SummaryResult, Citation
│   └── prompts.py         (~40 lines)  - SYSTEM_PROMPT + build_user_message()
├── tests/
│   ├── __init__.py
│   ├── test_level1.py     (~70 lines including comments)
│   └── test_level2.py     (~50 lines including comments)
├── evals/
│   └── judge_eval.py      (~120 lines)  - polished demo with rubric
├── exercises/
│   └── level1_prompts.md  (4–6 prompts)
├── sample_outputs/
│   ├── photosynthesis.json
│   └── quantum_computing.json
├── verify_setup.py        (~80 lines)
├── .env.example
├── requirements.txt       (with pin date noted)
└── README.md              (setup, choices, run instructions)
```

No `solution/` directory. No `DEFECTS.md` in this build.

---

## Risks Reassessed

1. **Anthropic SDK churn between build and June workshop.**
   The owner reserved the right to re-pin closer to the date. Mitigation: pin specific versions in `requirements.txt`, and add a "verify before workshop" line item in the README.

2. **Tavily quota exhaustion.**
   Each attendee has their own key, so per-attendee quotas matter. Free tier is generous, but Level 2 tests that retry will burn the quota fast. The plan should constrain Level 2 to 1 test stub and recommend running it sparingly.

3. **Native tool-use schema rejection.**
   Pydantic v2 schemas occasionally include constructs Anthropic's tool-use endpoint dislikes (e.g., `$ref`s, certain `anyOf` shapes). Mitigation: keep `SummaryResult` shallow (no nested optional unions), and the build engineer should test the round-trip once during Phase 5.

4. **Defect "too subtle" risk.**
   Obvious-by-omission is intended, but if reviewers feel the gap is too easy to miss, a fallback is to add a single comment in `agent.py`: `# (search results returned)` — placed where the check should be. Decide during the build, not in the plan.

5. **Workshop topic content drift.**
   The starter Level 2 test asks for a real summary of "photosynthesis." The model output is non-deterministic enough that even with `temperature=0`, the assertion threshold (`>= 2 findings`, `>= 1 citation`) is the right level of looseness. Don't tighten it.

---

## What Remains Open

Captured separately in `notes/Creation_Questions_v2.md`. Most relate to small ambiguities in the eval, the README, or workshop logistics — none block scaffolding.
