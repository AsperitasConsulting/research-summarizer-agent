# Implementation Thinking v1

**Date:** 2026-05-03
**Purpose:** Capture reasoning about the implementation plan before build begins.

---

## What This Project Is and Is Not

The Research Summarizer Agent is a workshop teaching vehicle, not a production system. Every architectural decision should be evaluated against one criterion: *can a workshop attendee understand the full agent behavior in under ten minutes, leaving the remaining time to write tests?*

This constraint is unusual and worth internalizing. It actively forbids patterns that would be good engineering in a production context — retries, caching, logging frameworks, streaming, multi-turn conversation. The agent's simplicity is a feature.

---

## The Implementation Plan Is Mature

The existing `plans/ImplementationPlan.md` is at version 5.0 and incorporates five rounds of question-and-answer with the project owner. The decisions table at the top of that plan locks every significant design choice. This thinking document does not re-open those decisions; it documents the reasoning for key choices that might otherwise look odd to a first reader.

---

## Key Design Choices and Their Rationale

### 1. Pydantic v2 for the data model

The spec leaves the choice open (Pydantic vs. plain dataclass). The implementation plan locks Pydantic v2 for one reason: `model_json_schema()` produces the tool schema for Anthropic's structured output endpoint without manual JSON wrestling. A plain dataclass would require hand-writing a JSON schema dict — more fragile and harder to keep in sync with the model definition.

The tradeoff: Pydantic v2 is a dependency attendees may not know. The workshop does not teach Pydantic, so the model code must be simple enough to skim past without understanding it.

### 2. Anthropic native `tool_use` for structured output (not `instructor`, not JSON mode)

The spec's structured-output requirement could be satisfied several ways: `instructor` library, JSON mode with manual parsing, or native tool_use. The plan chooses native tool_use because:

- It has no extra dependencies beyond the Anthropic SDK.
- The mechanism (force a tool call, parse the `tool_use` block) is teachable in the workshop as a pattern for agentic systems.
- `instructor` would add a third abstraction layer on top of Pydantic and Anthropic, which conflicts with the 10-minute comprehension goal.

The tradeoff: `tool_use` requires the schema to be shaped as an Anthropic tool definition, which is why `summary_result_tool_schema()` exists in `models.py` — to keep that translation out of `agent.py`.

### 3. Intentional defect Option A (missing `NoResultsError` guard)

The spec offers three defect options. Option A is the best choice for the workshop because:

- It is deterministic: the test either raises or it doesn't; no LLM variability.
- It is fast: Level 1 tests use `StubSearchTool`, so the test runs without any API call.
- It is pedagogically clear: the fix is exactly two lines of guard code, and the `# TODO: handle empty results` marker points attendees directly at the gap.
- It exercises the testing pyramid's central lesson: orchestration-layer defects are cheapest to catch at Level 1 with stubs, not at Level 2 with real API calls.

Option B (citation URL validation) and Option C (key_findings count) both require real API calls to surface, making them Level 2 defects. They are harder to demonstrate live and harder for attendees to write a deterministic test for.

### 4. Solutions written before stubs

The plan requires that `solution/tests/` be written and validated against both the correct and defective agent *before* `tests/` stubs are derived from them. This is a build discipline rule:

- It prevents writing stubs that are structurally incompatible with the solutions.
- It ensures the defect-catching test actually catches the defect before workshop day.
- The verbatim pytest output captured in `solution/DEFECTS.md` gives the instructor hard evidence to show attendees during the "why does testing work?" discussion.

### 5. Model pinned to `claude-haiku-4-5-20251001`, not an alias

Model pinning is itself a workshop teaching point. An aliased name like `claude-haiku-latest` can silently change behavior between the workshop build date and workshop day. The implementation plan is explicit that this pin must not be changed without owner sign-off.

The eval judge uses `claude-sonnet-4-6` for a different reason: the judge needs stronger reasoning capability than the summarizer, and Sonnet is the right capability tier for rubric evaluation. This model is also pinned (not aliased).

### 6. The `summarize()` function signature

The public API is `summarize(topic: str, search_tool: SearchTool | None = None) -> SummaryResult`. The optional `search_tool` parameter is the dependency injection seam that Level 1 tests rely on. Without it, tests would need to monkeypatch internals (fragile) or make real network calls (slow, non-deterministic, requires credentials).

The spec specifies this signature explicitly. The plan honors it without adding any additional parameters (no `model=`, no `temperature=`, no `client=` — those are read from environment variables, which tests override via `monkeypatch.setenv`).

---

## The 15-Phase Build Sequence

The implementation plan's 15 phases are not arbitrary. They follow a strict dependency order:

1. **Phases 1–6** build the agent bottom-up: scaffolding → types → tools → prompts → orchestration → package init.
2. **Phase 7** authors the complete solution tests while the agent is still in its correct (non-defective) state.
3. **Phase 8** validates the solution tests pass against the correct agent — a quality gate.
4. **Phase 9** inserts the defect and re-validates — proves the defect-catching test actually works.
5. **Phases 10–15** derive everything else from the now-validated core: stubs, eval, exercises, samples, setup script, README.

The two first-failure escalation gates (Phases 8 and 9) are the most important structural decisions in the build. They ensure no stub, sample, or documentation is produced from a foundation that hasn't been proven to work.

---

## Environment Status (as of this assessment)

All Python dependencies are present except `tavily-python`, which must be installed before Phases 3 and 8. See `plans/EnvironmentPreparation.md` for the full dependency and API key checklist.

- Python 3.12.3 satisfies the `>=3.11,<3.14` requirement.
- `anthropic 0.64.0` is installed. Verify `claude-haiku-4-5-20251001` and `claude-sonnet-4-6` are accessible with the provided keys before Phase 5.
- `tavily-python` is not installed. Install before starting Phase 3.

---

## Risks Worth Monitoring

1. **Anthropic model availability.** The plan pins `claude-haiku-4-5-20251001`. If this model has been deprecated or renamed in the current SDK, Phase 5 will surface it immediately. The escalation rule (first failure, no silent fallback) applies.

2. **Tavily API surface.** The plan assumes `client.search(query=..., max_results=...)` returns a response with `title`, `url`, and `snippet` fields. If the Tavily client API has changed since the plan was written, Phase 3 escalation criteria apply.

3. **Pydantic schema shape.** The `model_json_schema()` output from Pydantic v2 must be compatible with Anthropic's tool-use endpoint. This has been validated in similar projects but should be confirmed in Phase 5 during the first real LLM call.

4. **Level 2 test flakiness.** `test_result_fields_populated` uses real Anthropic with `temperature=0` and a deterministic stub for search. If this test proves flaky across runs, the Phase 8 escalation rule fires and the plan has a documented fallback (replace with a structural recording-stub test).
