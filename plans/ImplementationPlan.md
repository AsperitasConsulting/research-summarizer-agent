# Implementation Plan: Research Summarizer Agent

**Version:** 3.0
**Based on:**
- `requirements/Research_Summarizer_Agent_Spec.md` v1.0 draft
- `requirements/Testing-Pyramid.md`
- `notes/Creation_Thinking_v3.md` (this revision)
- `notes/Creation_Questions_v1.md` (with project-owner answers inline)
- `notes/Creation_Questions_v2.md` (with project-owner answers inline)
**Purpose:** Workshop teaching vehicle for the AI Agent Testing Pyramid (90-minute session)

---

## Guiding Principle

Every decision optimizes for **workshop clarity**, not production quality. If something makes the code harder to understand in 10 minutes, it is wrong. If it makes the workshop run long, it is wrong. The 90-minute clock — with 30–45 minutes of attendee coding inside it — is the benchmark for "is this scoped right?"

Two structural rules govern this revision:

1. **Solutions are written and proven before stubs are produced.** No attendee-facing test stub ships in this build until its full solution has been authored, run, and shown to behave correctly against both the corrected agent (must pass) and the defective agent (the defect-catching test must fail; all others must still pass).
2. **Each phase has explicit human-escalation triggers.** When the agent team hits one, it stops and asks. The triggers are concrete per phase; cross-cutting triggers are listed once at the bottom of this plan.

---

## Decisions Locked In

| Decision | Choice | Source |
|----------|--------|--------|
| Data model | Pydantic v2 (`>= 2.7, < 3`) | Q7 v1 |
| Structured output | Anthropic native `tool_use` (force `tool_choice`) | Q8 v1 |
| Intentional defect | Option A (no `NoResultsError` on empty results) | Q12 v1, recommended in spec |
| Defect implementation style | Missing code block **with a leading comment marker** at the gap | Q4 v2 (revised from v2 plan) |
| Solutions in this build | **Written, verified, then converted to stubs** (new in v3) | Owner instruction (this turn) |
| `solution/` directory | Default in plan: kept in repo, marked instructor-only. Open in v3 questions | New in v3 |
| `DEFECTS.md` | Produced in this build alongside the validated solutions | Q13 v1 |
| Pytest commenting | Extensive — starter files double as pytest tutorials | Q1 v1 |
| Workshop coding budget | 30–45 min → Level 1 = 1 passing test + 3–4 stubs; Level 2 = 1 stub | Q2 v1 |
| Tavily | Required (each attendee brings own free-tier key, supplied at workshop) | Q3 v1, Q1/Q2 v2 |
| Anthropic SDK | Latest stable at build time, may re-pin closer to June workshop | Q5 v1 |
| Python | `>=3.11, <3.14` | Q6 v1 |
| Sample outputs | JSON, **2 topics**, **real-but-stable URLs** | Q9 v1, Q6/Q7 v2 |
| Level 1 prompts | Prompts attendees paste into Claude Code, **conversational voice** | Q10 v1, Q13 v2 |
| **Level 2 prompts** | Same as Level 1 — produce a parallel `level2_prompts.md` | Q12 v2 (new) |
| Eval audience | Instructor-run during Segment 5; attendees can run after | Q11 v1 |
| Eval judge model | `claude-sonnet-4-6`, pinned in a constant | Q8 v2 |
| Eval rubric | Pass/fail per dimension | Q9 v2 |
| Eval trace artifact | **Write run output to `sample_outputs/judge_eval_run.json`** | Q11 v2 (new) |
| `verify_setup.py` Tavily check | Trust the key — do not call | Q16 v2 |
| `verify_setup.py` output | **Verbose with diagnostic detail** (versions, etc.) | Q17 v2 |
| `requirements-lock.txt` | **Generate and commit** alongside `requirements.txt` | Q18 v2 |
| Repo directory name | Leave as `research-summarizer-agent/` | Q19 v2 |
| Branding/attribution | None | Q20 v2 |

---

## Phase 1: Project Scaffolding

**Goal:** Establish file structure and dependency baseline so everything imports cleanly from day one.

### 1.1 Directory Structure

```
research-summarizer-agent/         (existing working dir; do not rename)
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   ├── models.py
│   └── prompts.py
├── solution/                      (instructor-only — see solution/README.md)
│   ├── README.md
│   ├── DEFECTS.md
│   └── tests/
│       ├── __init__.py
│       ├── test_level1.py         (full solutions)
│       └── test_level2.py         (full solutions)
├── tests/
│   ├── __init__.py
│   ├── test_level1.py             (commented stubs derived from solution/)
│   └── test_level2.py             (commented stub derived from solution/)
├── evals/
│   └── judge_eval.py
├── exercises/
│   ├── level1_prompts.md
│   └── level2_prompts.md
├── sample_outputs/
│   ├── photosynthesis.json
│   ├── quantum_computing.json
│   └── judge_eval_run.json        (produced by Phase 11)
├── verify_setup.py
├── .env.example
├── requirements.txt
├── requirements-lock.txt
└── README.md
```

### 1.2 `requirements.txt` and `requirements-lock.txt`

Top-level pins in `requirements.txt` (initial bounds — replace with exact resolved versions at build time):

```
anthropic>=X.Y.Z,<NEXT_MAJOR     # latest stable as of build date; record date in README
pydantic>=2.7,<3
tavily-python>=0.5,<1
pytest>=8,<9
python-dotenv>=1,<2
```

Build engineer **must**:

1. Create a fresh virtualenv.
2. `pip install -r requirements.txt` to resolve current versions.
3. Replace placeholder pins above with the exact `==X.Y.Z` versions resolved.
4. Run `pip freeze > requirements-lock.txt` to capture the full transitive closure.
5. Record the pin date in the README ("Pinned 2026-MM-DD; refresh before workshop date if more than ~30 days old").
6. Commit both `requirements.txt` (top-level pins) and `requirements-lock.txt` (full closure).

### 1.3 `.env.example`

```
# Required
ANTHROPIC_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here

# Optional (instructor overrides)
# SUMMARIZER_MODEL=claude-haiku-4-5-20251001
# SUMMARIZER_TEMPERATURE=1.0
```

### 1.4 Python Version Floor

Document `>=3.11,<3.14` in the README and have `verify_setup.py` enforce the range at runtime.

### 1.5 Escalation Criteria — Phase 1

Escalate to a human if any of:

- `pip install -r requirements.txt` fails to resolve a working set within two attempts (e.g., a transitive conflict between Anthropic SDK and Pydantic versions). Do **not** loosen pins to escape — the spec requires explicit version control.
- Anthropic SDK's "latest stable" no longer supports `claude-haiku-4-5-20251001` (model deprecation, response-shape change). The pinned model is a teaching point and cannot be silently swapped.
- The directory structure as drafted collides with an existing path that contains owner work (e.g., the `solution/` path exists and is non-empty before this build started).

---

## Phase 2: Data Model — `agent/models.py`

**Goal:** Define `SummaryResult` and `Citation` using Pydantic v2.

### Tasks

1. `Citation(BaseModel)` — fields: `title: str`, `url: str`, `snippet: str`.
2. `SummaryResult(BaseModel)` — fields: `topic: str`, `synopsis: str`, `key_findings: list[str]`, `citations: list[Citation]`.
3. **No** field validators or constraints — all bounds (synopsis sentence count, findings count, citation URL provenance) are enforced via the prompt only, per spec.
4. Provide a module-level helper `summary_result_tool_schema() -> dict` that returns `SummaryResult.model_json_schema()` shaped for Anthropic tool-use input. Reason: keep schema-shape munging out of `agent.py`.

**Estimated size:** ~30 lines.

### Escalation Criteria — Phase 2

Escalate if:

- The Pydantic v2 schema produced by `model_json_schema()` includes constructs Anthropic's tool-use endpoint rejects (`$ref`, deeply nested `anyOf`, etc.) and a single shape adjustment (e.g., flattening a `Union`) does not fix it. Do not silently switch off Pydantic v2 or fall back to JSON-mode.
- Pydantic v2 emits validation behavior (e.g., automatic coercion) that the spec's "no field validators" rule turns out to depend on subtly. Surface the conflict; do not paper over.

---

## Phase 3: Search Tool — `agent/tools.py`

**Goal:** Define the `SearchTool` protocol, both implementations, and the related exceptions.

### Tasks

1. Define `SearchResult` as a Pydantic model — `title`, `url`, `snippet`.
2. Define exceptions:
   - `class SearchToolError(Exception): pass`
   - `class NoResultsError(Exception): pass`
3. Define `SearchTool(Protocol)` with `search(query: str, max_results: int = 5) -> list[SearchResult]`.
4. Implement `TavilySearchTool`:
   - Reads `TAVILY_API_KEY` at construction time (not on every call).
   - Calls Tavily Search API with a 10-second timeout.
   - Wraps any underlying client exception in `SearchToolError`.
   - Returns an empty list (not an exception) for zero results.
5. Implement `StubSearchTool`:
   - Constructor accepts `results: list[SearchResult]`.
   - `search()` returns the pre-configured list regardless of query/`max_results`.
   - Importable as `from agent.tools import StubSearchTool, SearchResult, NoResultsError, SearchToolError`.

**Estimated size:** ~90 lines.

### Escalation Criteria — Phase 3

Escalate if:

- `tavily-python` API surface differs from the documented `client.search(query=..., max_results=...)` shape and the change is non-obvious.
- Tavily returns a structured response that does not map cleanly to the three `SearchResult` fields without inventing data (e.g., `snippet` field renamed/removed). Do not synthesize fields.
- A timeout or error mode arises that does not fit `SearchToolError` cleanly. Do not invent a second exception class without owner approval.

---

## Phase 4: Prompts — `agent/prompts.py`

**Goal:** Isolate prompt text so it is easy to read, test, and modify.

### Tasks

1. `SYSTEM_PROMPT` constant — exact text from spec (no paraphrasing).
2. `build_user_message(topic: str, results: list[SearchResult]) -> str` — formats per spec template:
   ```
   Topic: {topic}

   Search Results:
   [1] {title}
   URL: {url}
   {snippet}

   [2] {title}
   ...

   Return a structured summary following the required schema.
   ```
3. No conditional logic for empty results — the seeded defect (Phase 5) intentionally lets an empty list reach this function.

**Estimated size:** ~40 lines.

### Escalation Criteria — Phase 4

Escalate if:

- Any rewording of the system prompt is necessary to make structured output work (e.g., the model otherwise refuses to use the tool). The spec explicitly fixes the system prompt; changes need owner approval.
- The user-message template format produces ambiguous parsing for unusual snippets (e.g., snippets containing `[N]` markers). Do not silently escape — flag the ambiguity.

---

## Phase 5: Agent Orchestration — `agent/agent.py` (CORRECT version first)

**Goal:** Implement `summarize()` as a five-step pipeline. **Phase 5 produces the corrected agent (with the empty-results guard in place).** Phase 9 will re-introduce the defect for shipping.

### Tasks

1. Implement `summarize(topic: str, search_tool: SearchTool | None = None) -> SummaryResult`:

   **Step 1 — Validate input**
   - `topic = topic.strip()`
   - `if not topic: raise ValueError("topic must be non-empty")`

   **Step 2 — Execute search**
   - If `search_tool is None`, call `_default_search_tool()`.
   - `results = search_tool.search(topic, max_results=5)`
   - **In Phase 5 (correct version):** include the guard:
     ```python
     if not results:
         raise NoResultsError(topic)
     ```

   **Step 3 — Build prompt**
   - `user_message = build_user_message(topic, results)`

   **Step 4 — Call LLM**
   - Read `SUMMARIZER_MODEL` env var (default `"claude-haiku-4-5-20251001"`).
   - Read `SUMMARIZER_TEMPERATURE` env var (default `1.0`, parsed as float).
   - Build a single Anthropic tool from `summary_result_tool_schema()`.
   - Call `client.messages.create(...)` with `tool_choice={"type": "tool", "name": "return_summary"}`.

   **Step 5 — Parse and return**
   - Find the `tool_use` block in `response.content`.
   - Validate via `SummaryResult.model_validate(block.input)`.
   - Return the model instance.
   - Let `anthropic.APIError` and `pydantic.ValidationError` propagate unwrapped.

2. Implement `_default_search_tool()`:
   ```python
   def _default_search_tool() -> SearchTool:
       if os.environ.get("TAVILY_API_KEY"):
           return TavilySearchTool()
       return StubSearchTool(results=[])
   ```

**Estimated size:** ~70 lines (with the guard; without the guard the file is 2 lines shorter).

### Escalation Criteria — Phase 5

Escalate if:

- The Anthropic tool-use round-trip (force tool, parse `tool_use` block, `model_validate`) fails after one schema-shape adjustment. Do not move to JSON mode or `instructor` library without owner approval — the spec choice was deliberate.
- The pinned model name returns a "model not found" or deprecation error. Do not fall back to an alias such as `claude-haiku-latest`; the spec forbids it.
- Step 5 reliably encounters `pydantic.ValidationError` at `temperature=1.0` for plausible search inputs. The spec's "no retry" rule means the agent will surface these to attendees — but a high baseline failure rate would compromise the workshop.

---

## Phase 6: Package Init — `agent/__init__.py`

**Goal:** Single clean public API surface.

### Tasks

1. `from agent.agent import summarize`
2. `from agent.models import SummaryResult, Citation`
3. `from agent.tools import SearchTool, StubSearchTool, SearchResult, SearchToolError, NoResultsError`
4. Verify `from agent import summarize` works (spec requirement).

**Estimated size:** ~10 lines.

### Escalation Criteria — Phase 6

Escalate if:

- An import cycle appears between `agent.py` and any sibling module. The current design avoids it; if one shows up, the design has drifted and needs review.

---

## Phase 7: Author Solution Tests — `solution/tests/`

**Goal:** Write the **complete, working** Level 1 and Level 2 test suites that the validation steps (Phase 8 and Phase 9) will run.

### 7.1 `solution/README.md`

A short, blunt warning:

```
This directory contains the instructor reference implementation of the Research
Summarizer Agent test suite. It is NOT for workshop attendees.

If you are an attendee: please ignore this directory. Open `tests/` instead.

The contents of this directory:
  - tests/test_level1.py — completed Level 1 solutions
  - tests/test_level2.py — completed Level 2 solution
  - DEFECTS.md           — which defect was seeded into the agent and the fix
```

### 7.2 `solution/tests/test_level1.py`

The full suite the v2 plan described as commented stubs — but here, uncommented and runnable.

Imports: `pytest`, `summarize`, `StubSearchTool`, `SearchResult`, `NoResultsError`, `SearchToolError` from `agent`.

Fixture:
```python
@pytest.fixture
def stub_results():
    return [
        SearchResult(title="...", url="https://example.com/a", snippet="..."),
        SearchResult(title="...", url="https://example.com/b", snippet="..."),
    ]
```

Tests (all four written, all four pass against the corrected Phase 5 agent):

1. `test_empty_topic_raises_value_error` — `summarize("")` raises `ValueError`.
2. `test_no_results_raises_no_results_error` — inject `StubSearchTool(results=[])`, expect `NoResultsError`. **This is the defect-catching test.**
3. `test_search_tool_error_propagates` — inject a stub whose `.search()` raises `SearchToolError`; expect propagation.
4. `test_result_fields_populated` — inject `stub_results`, call `summarize(...)`, assert `result.topic`, `result.synopsis`, `result.key_findings`, and `result.citations` are present and non-empty. (Note: this calls real Anthropic; document the API-key requirement at the top.)

> Decision point: if `test_result_fields_populated` proves flaky during validation, replace it (in both solution and stubs) with a structural test using a recording stub that asserts `search_tool.search()` was called exactly once with the expected args. Decision is made during Phase 8 based on observed behavior.

**Estimated size:** ~90 lines (no commenting-out).

### 7.3 `solution/tests/test_level2.py`

Constants and skip guard at top:
```python
TEST_MODEL = "claude-haiku-4-5-20251001"
TEST_TEMPERATURE = 0

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get("TAVILY_API_KEY"),
    reason="Level 2 tests require ANTHROPIC_API_KEY and TAVILY_API_KEY",
)
```

One test (uncommented, runnable):

```python
def test_photosynthesis_summary(monkeypatch):
    monkeypatch.setenv("SUMMARIZER_MODEL", TEST_MODEL)
    monkeypatch.setenv("SUMMARIZER_TEMPERATURE", str(TEST_TEMPERATURE))
    result = summarize("photosynthesis")
    assert len(result.key_findings) >= 2
    assert len(result.citations) >= 1
```

**Estimated size:** ~30 lines.

### Escalation Criteria — Phase 7

Escalate if:

- The owner has not provided a build-time `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`. Phase 8 cannot validate the Level 2 solution without them. Do not skip the validation; ask.
- `test_result_fields_populated` requires a non-trivial change to compile or run (beyond the documented decision-point alternative). Stop and discuss whether the test belongs at Level 1 or should move to Level 2.

---

## Phase 8: Validate Solutions Against the Corrected Agent

**Goal:** Prove that every solution test passes against the Phase 5 (correct) agent. This is the gate before the defect is seeded.

### Steps

1. Confirm Phase 5 agent has the empty-results guard in place.
2. Run `pytest solution/tests/test_level1.py -v` from the repo root.
3. Run `pytest solution/tests/test_level2.py -v` (requires both API keys present).
4. **All seven tests** (4 Level 1 + 1 Level 2 + however many implicit checks the runner exposes) must pass. Capture the run summary.
5. Re-run Level 2 once more to detect flakiness. If pass/fail differs across runs, the assertion threshold or temperature handling is wrong — escalate.

### Escalation Criteria — Phase 8

Escalate if:

- Any solution test fails against the corrected agent. Do **not** loosen the test or modify the agent to make it pass without explicit owner sign-off — that would defeat the validation's purpose.
- Any Level 2 test produces a different outcome across two consecutive `temperature=0` runs on the same input. The assertion is too tight, the prompt is unstable, or the search-tool output is varying — none of these are silently fixable.
- A test passes but emits warnings that suggest it is testing the wrong thing (e.g., `pytest` warnings about a fixture not being used, or imports that resolve unexpectedly).

---

## Phase 9: Seed the Defect and Re-validate

**Goal:** Insert the workshop's intentional defect into `agent/agent.py`, then prove the solution suite catches it as designed.

### 9.1 Defect Insertion

In `agent/agent.py`, **remove** the empty-results guard added in Phase 5. Replace it with a **single-line comment marker** at the gap, per the Q4 v2 answer:

```python
results = search_tool.search(topic, max_results=5)
# (handle empty results before prompting)
user_message = build_user_message(topic, results)
```

The exact wording of the marker comment is open in `Creation_Questions_v3.md` — the line above is the placeholder this plan uses; the build engineer should treat it as provisional pending owner confirmation.

### 9.2 Re-validation

1. Run `pytest solution/tests/test_level1.py -v`.
2. Expect: `test_no_results_raises_no_results_error` **fails**; the other three pass.
3. Run `pytest solution/tests/test_level2.py -v`.
4. Expect: `test_photosynthesis_summary` continues to pass (the defect does not affect topics with real results).
5. Capture the run summary as evidence in `solution/DEFECTS.md`.

### 9.3 `solution/DEFECTS.md`

```markdown
# Seeded Defect Reference (Instructor Only)

## Defect

Option A — `summarize()` does not raise `NoResultsError` when the search tool
returns an empty list. The agent instead lets the empty list flow into the
prompt-building step and calls the LLM with no results.

## Why this defect

- Deterministic, no API key required to surface (Level 1 catches it with a stub).
- Surfaces a real testing-pyramid teaching moment: orchestration logic gaps are
  caught by the unit-test base, not by model evals.

## Where it lives

`agent/agent.py`, in `summarize()`, immediately after the `search_tool.search(...)`
call. The marker comment `# (handle empty results before prompting)` is the only
hint in the source; no `TODO`, no docstring note.

## Which test catches it

`solution/tests/test_level1.py::test_no_results_raises_no_results_error`
(and its commented stub equivalent in `tests/test_level1.py`, once an attendee
fills it in).

## The fix

Add the two-line guard between the search call and the prompt build:

```python
results = search_tool.search(topic, max_results=5)
if not results:
    raise NoResultsError(topic)
user_message = build_user_message(topic, results)
```

## Validation evidence

- Solution Phase 8 run (corrected agent): all tests pass.
- Solution Phase 9 run (defective agent): only
  `test_no_results_raises_no_results_error` fails.
```

### Escalation Criteria — Phase 9

Escalate if:

- Any test other than `test_no_results_raises_no_results_error` fails against the defective agent. The defect's blast radius is wider than designed — fixing it silently would mask the real issue.
- `test_no_results_raises_no_results_error` continues to pass against the defective agent. Either the defect did not actually take effect (e.g., guard inadvertently still present elsewhere) or the test is not exercising what it claims.
- Behavior under the defect is non-deterministic (e.g., LLM happens to refuse the no-results prompt sometimes). The defect must produce a consistent symptom or its teaching value collapses.

---

## Phase 10: Convert Validated Solutions to Attendee Stubs — `tests/`

**Goal:** Produce `tests/test_level1.py` and `tests/test_level2.py` as commented-stub starters, derived directly from the validated solutions in `solution/tests/`.

### 10.1 `tests/test_level1.py`

- Copy the imports, header docstring, and fixture from the solution file. The header docstring expands here to teach pytest fundamentals (fixtures, `pytest.raises`, what an arrange/act/assert structure looks like) — attendees who are new to pytest meet these concepts first in the stub file, not in the solution.
- Keep `test_empty_topic_raises_value_error` **uncommented** and passing — this is the example test the stubs are modeled after.
- Convert each of the other three solution tests into commented-out shells using arrange/act/assert narration:
  ```python
  # def test_no_results_raises_no_results_error():
  #     # Arrange: build a StubSearchTool with an empty results list
  #     # Act: call summarize() with that tool
  #     # Assert: pytest.raises(NoResultsError) wraps the call
  #     pass
  ```
- Do **not** include the assertion bodies, the exact stub construction, or the fixture call patterns in the comments — those are what attendees write.

### 10.2 `tests/test_level2.py`

- Copy constants and skip guard from the solution file.
- Convert the single `test_photosynthesis_summary` solution into a commented shell with a header comment explaining why model and temperature are pinned (workshop teaching point).
- Include a sentence-long note that this test costs a real Anthropic + Tavily call per run — attendees should run it sparingly to preserve their free-tier quota.

**Estimated combined size:** ~90 lines (Level 1) + ~50 lines (Level 2), including comments.

### Escalation Criteria — Phase 10

Escalate if:

- A solution test cannot be reduced to a meaningful stub without either (a) revealing the answer or (b) leaving an attendee with too little to work from. The test is the wrong shape for a stub — discuss replacing it.
- Any commented stub fails to import or causes pytest collection errors. Stubs must compile cleanly even before an attendee uncomments them.

---

## Phase 11: Evals — `evals/judge_eval.py`

**Goal:** Pre-built LLM-as-judge demo for workshop Segment 5; instructor-run during the workshop, attendee-runnable afterwards. Writes a trace artifact to `sample_outputs/judge_eval_run.json`.

### Tasks

1. **Topic:** Hard-code one topic the agent generally handles well (e.g., "the discovery of penicillin"). Single run, not a sweep.
2. **Judge model:** `claude-sonnet-4-6` (constant at top of file, pinned).
3. **Rubric (pass/fail per dimension):**
   - **Factual accuracy** — synopsis and key findings consistent with each other and the cited snippets.
   - **Citation integrity** — every cited URL appears in the search-tool output passed to the agent.
   - **Synopsis quality** — 2–4 sentences, on-topic, no opinions.
   - **Findings count** — 2–5 substantive findings.
4. **Output to stdout** — labelled blocks for: agent result, judge prompt, judge verdict per dimension, overall pass count.
5. **Output to file** — write `sample_outputs/judge_eval_run.json` containing the same content as a structured JSON document. Schema:
   ```json
   {
     "topic": "...",
     "agent_model": "claude-haiku-4-5-20251001",
     "judge_model": "claude-sonnet-4-6",
     "search_results": [...],
     "agent_result": {...},
     "judge_prompt": "...",
     "judge_verdicts": {
       "factual_accuracy": "pass" | "fail",
       "citation_integrity": "pass" | "fail",
       "synopsis_quality": "pass" | "fail",
       "findings_count": "pass" | "fail"
     },
     "overall_score": "X/4",
     "run_at": "ISO-8601 timestamp"
   }
   ```
6. **Comments:** Each rubric dimension explained inline so attendees can study it later.
7. **Idempotent:** No caching, no flags. Running `python evals/judge_eval.py` from repo root with both API keys set just works. Re-running overwrites the JSON trace.

**Estimated size:** ~150 lines including comments.

### Escalation Criteria — Phase 11

Escalate if:

- `claude-sonnet-4-6` is not available at build time. Do not silently fall back to a different Sonnet pin — owner confirmed this exact model in Q8 v2.
- The judge produces inconsistent verdicts across two runs on the same input. Calibration is off, prompt is unclear, or the rubric is ambiguous — none are quietly fixable.
- The JSON trace artifact path conflicts with sample-output naming conventions in a way that confuses attendees (e.g., they mistake it for a hand-curated example). Discuss naming.

---

## Phase 12: Exercises — `exercises/level1_prompts.md` and `exercises/level2_prompts.md`

**Goal:** Suggested prompts attendees paste into Claude Code while writing tests at each level. Conversational voice (Q13 v2).

### 12.1 `exercises/level1_prompts.md`

4–6 prompts mapped 1:1 to the Level 1 stubs:

- "I'm working on a test that needs to confirm `summarize('')` raises a `ValueError`. The agent already exposes `StubSearchTool`, so I shouldn't need to make any real API calls — can you walk me through the test?"
- "I want to verify that when the search tool returns no results, `summarize()` raises `NoResultsError`. How would I set up a `StubSearchTool` with an empty list to make that happen?"
- "Could you help me write a test where the search tool itself raises `SearchToolError` from inside `.search()`, and we want to confirm `summarize()` lets that exception propagate?"
- "I'd like a test that checks the shape of a successful `SummaryResult` — that all four fields are populated and non-empty when `summarize()` is given the `stub_results` fixture."
- (Optional 5th/6th prompts — e.g., parametrizing the empty-topic test for whitespace inputs, or a recording-stub variant.)

Each prompt:

- Conversational opening ("I'm working on…", "I want to verify…", "Could you help me…").
- States the goal and the agent surface area being used; never includes the assertion code.
- Reads as something an attendee could paste verbatim into Claude Code.

### 12.2 `exercises/level2_prompts.md`

1–2 prompts mapped to the Level 2 stub:

- "I'm trying to write a constrained-model test for the photosynthesis topic. The agent needs to be invoked with `temperature=0` and the pinned Haiku model. How should I set up the test so it reads cleanly and asserts on the shape of the result rather than exact text?"
- (Optional) "Help me think through what additional Level 2 assertions might be worth adding — without making the test brittle to model wording variation."

### Escalation Criteria — Phase 12

Escalate if:

- A prompt naturally elicits an answer from Claude Code that diverges materially from the validated solution test (e.g., it suggests mocking the Anthropic client at Level 2). Reword or remove rather than ship a prompt that misleads.
- The conversational voice constraint produces prompts that read awkwardly when paired with an attendee's existing test scaffolding.

---

## Phase 13: Sample Outputs — `sample_outputs/`

**Goal:** Concrete examples of `SummaryResult` shape and quality, using **real, stable URLs** (Q6 v2).

### Tasks

1. `photosynthesis.json` — simple, factual topic. 3 key findings, 3 citations.
2. `quantum_computing.json` — technical, multi-perspective topic. 4 key findings, 4 citations.
3. **Citation URLs:** Real but stable. Preferred sources (in order): Wikipedia article URLs, NIH/NCBI publication landing pages, NASA or DOE program pages, peer-reviewed open-access DOIs. Avoid news articles, blogs, and any URL that looks event-specific.
4. **Pre-workshop link check:** Add a one-line note in the README that the build engineer (or owner) should curl each URL before the workshop date and replace any that 404 or redirect.
5. Each file is a hand-curated, valid `SummaryResult` JSON serialization (importable via `SummaryResult.model_validate_json(open(...).read())` as a sanity check during build).

### Escalation Criteria — Phase 13

Escalate if:

- No stable, common URLs can be found for both topics that satisfy the "unlikely to change" criterion. Discuss whether to swap topics or revisit Q6 v2.
- A sample, when validated through `SummaryResult.model_validate_json(...)`, fails parse — schema drift between this file and `models.py` shouldn't exist.

---

## Phase 14: Verify Setup — `verify_setup.py`

**Goal:** Pre-workshop self-check that fails loudly with actionable messages and **prints diagnostic detail** (Q17 v2).

### Checks (in order, each printed with PASS/FAIL/WARN prefix and diagnostic info)

1. Python version `>= 3.11` and `< 3.14`. Print the actual `sys.version`.
2. All packages in `requirements.txt` import cleanly. Print the resolved version of each.
3. `ANTHROPIC_API_KEY` is set and non-empty. Print key-prefix-masked confirmation (e.g., `sk-ant-...XYZ`).
4. Minimal Anthropic API call (single-token completion) succeeds. Print the model used and the elapsed time.
5. `TAVILY_API_KEY` presence — PASS if set (no live call, per Q16 v2), WARN if absent. Print key-prefix-masked confirmation if present.

### Behavior

- Exit code `0` on full pass (all PASS, optional WARN allowed).
- Exit code `1` on any FAIL.
- Each FAIL includes a remediation hint (e.g., "FAIL: ANTHROPIC_API_KEY not set. Add it to your .env file or export it: `export ANTHROPIC_API_KEY=sk-ant-...`").
- Output is plain text suitable for screen-sharing.

**Estimated size:** ~120 lines.

### Escalation Criteria — Phase 14

Escalate if:

- The "minimal Anthropic API call" check exposes a billing or org-permissions edge case that the keys provided to attendees won't have access to.
- Diagnostic output prints anything that looks like a leaked secret. Mask aggressively; if the masking heuristic is in doubt, ask.

---

## Phase 15: Documentation — `README.md`

**Goal:** Single onboarding doc for attendees and instructors, **narrowly scoped** (Q14 v2).

### Sections (in order)

1. **What this is** — single paragraph: workshop teaching vehicle, not production.
2. **Prereqs** — Python 3.11–3.13. Note that workshop organizers supply Anthropic and Tavily keys (Q1/Q2 v2).
3. **Setup** — `python -m venv`, activate, `pip install -r requirements.txt`, copy `.env.example` to `.env`, fill in keys, `python verify_setup.py`.
4. **How the agent works** — link to `requirements/Research_Summarizer_Agent_Spec.md`. Two-paragraph summary inline.
5. **Running tests** — `pytest tests/test_level1.py`, `pytest tests/test_level2.py`.
6. **Running the eval** — `python evals/judge_eval.py`; mention the `sample_outputs/judge_eval_run.json` trace artifact.
7. **Design choices** — Pydantic v2 + native tool_use rationale. Pin date.
8. **Pin-refresh playbook (Q15 v2)** — exact commands:
   ```
   pip install -U anthropic pydantic tavily-python pytest python-dotenv
   pip freeze > requirements-lock.txt
   # Manually update top-level pins in requirements.txt to match new versions.
   ```
9. **Sample output URL convention** — real, stable URLs (Wikipedia/NIH/etc.); pre-workshop link check note.
10. **Troubleshooting** — common failures from `verify_setup.py` mapped to fixes.
11. **Note for attendees:** `solution/` directory exists for instructor reference; attendees should ignore it.

**Note:** `solution/DEFECTS.md` is **not** referenced from this README — it is purely an instructor reference.

### Escalation Criteria — Phase 15

Escalate if:

- The README grows beyond a single screen of setup steps for attendees (the narrow-focus rule from Q14 v2). Trim or move material into linked files.
- The pin-refresh playbook commands diverge from what `requirements-lock.txt` actually captured (e.g., a transitive dep that doesn't get updated by the listed `pip install -U` line).

---

## Implementation Order and Dependencies

| Order | Phase | Depends On | Why this order |
|-------|-------|------------|----------------|
| 1 | Scaffolding | — | Everything needs the directories and pinned deps |
| 2 | Models | 1 | Types are referenced by tools, prompts, agent, eval |
| 3 | Tools | 2 | Uses `SearchResult` + defines exceptions |
| 4 | Prompts | 2, 3 | Formats `SearchResult` lists into messages |
| 5 | Agent (correct) | 2–4 | Wires everything; defect NOT yet inserted |
| 6 | Package init | 5 | Re-exports from completed modules |
| 7 | Author solutions | 6 | Need `from agent import ...` to work |
| 8 | **Validate solutions vs. correct agent** | 5, 7 | Gate: all solutions must pass |
| 9 | **Seed defect + re-validate** | 8 | Gate: only the defect-catching test fails |
| 10 | Convert solutions to stubs | 9 | Stubs derived from validated solutions |
| 11 | Evals | 6 | Calls `summarize()`; uses Sonnet judge |
| 12 | Exercises | 10 | Mirrors stub tests |
| 13 | Sample outputs | 2 | JSON serializations of `SummaryResult` |
| 14 | Verify setup | 1 | Standalone script; depends only on installed deps |
| 15 | README | All | Describes the finished project |

---

## Cross-Cutting Escalation Protocol

Independent of any single phase, the agent team escalates to a human when **any** of the following occur:

1. **Two-strike rule.** A discrete attempt at a single task fails twice with no new diagnostic information surfaced between attempts.
2. **Spec / answers contradiction.** Two of (the spec, `Creation_Questions_v1.md`, `Creation_Questions_v2.md`, `Creation_Questions_v3.md`, this plan) disagree about a requirement.
3. **Out-of-band dependency behavior.** Anthropic SDK, Tavily, or Pydantic emit behavior that is not documented here and does not have an obvious resolution within the spec.
4. **Model-nondeterminism rule.** Any Level 2 or eval result that varies meaningfully across two consecutive runs at `temperature=0` on identical inputs.
5. **Scope drift.** Any time the team would need to add a feature, abstraction, file, or dependency not explicitly authorized by the spec, this plan, or owner answers. Examples that **always** escalate: caching, retries, logging frameworks, CLI surface beyond `verify_setup.py`, additional models, additional search tools.
6. **Secret-leak risk.** Any diagnostic output, sample file, or commit candidate that might contain an API key or credential.
7. **Validation gate failure.** Phase 8 or Phase 9 produces an unexpected outcome (any test fails when it should pass, or vice versa, or the failure pattern in Phase 9 is wider or narrower than the single defect-catching test).

### How to Escalate

- Stop the in-progress task immediately.
- Do not commit the in-progress state to the main branch.
- Surface to the human a short note containing: the phase, the trigger that fired, what was attempted, the observed result, and the team's best guess at the cause.
- Wait for human direction before resuming. Do not auto-retry past the two-strike threshold.

---

## Verification Criteria

Before declaring the build complete:

- [ ] `python verify_setup.py` exits 0 with all keys present (with diagnostic detail printed); exits 1 if Anthropic key missing.
- [ ] **Phase 8 evidence:** all solution tests pass against the corrected Phase 5 agent (run summary captured in `solution/DEFECTS.md`).
- [ ] **Phase 9 evidence:** with the defect re-introduced, only `test_no_results_raises_no_results_error` fails; all other solution tests still pass (run summary captured in `solution/DEFECTS.md`).
- [ ] `pytest tests/test_level1.py` runs cleanly: 1 test passes; commented stubs are no-ops, not import errors.
- [ ] `pytest tests/test_level2.py` skips cleanly when `ANTHROPIC_API_KEY` is unset; runs successfully (after attendees uncomment) when keys are present.
- [ ] `from agent import summarize, SummaryResult` works.
- [ ] A live `summarize("photosynthesis")` returns a valid `SummaryResult` with non-empty fields.
- [ ] `python evals/judge_eval.py` produces readable stdout output and writes `sample_outputs/judge_eval_run.json` with the documented schema.
- [ ] Every `agent/*.py` file is under 100 lines (well under the 500-line CLAUDE.md ceiling).
- [ ] No secrets in committed code; `.env.example` documents every variable.
- [ ] Pin date recorded in README; pin-refresh playbook present; `requirements.txt` and `requirements-lock.txt` both committed.
- [ ] `solution/` directory present with `README.md` warning header, `DEFECTS.md`, and validated test files (subject to v3 question Q1 — owner may direct relocation).
- [ ] No phase escalation outstanding.

---

## Out of Scope (Reaffirmed from Spec)

- Multi-turn conversation, session state, memory.
- Caching, deduplication, retry/backoff, rate limiting.
- Streaming.
- UI / CLI beyond `verify_setup.py`.
- Logging frameworks (print is fine).
- Auth beyond env-var API keys.

---

*Document version: 3.0 — incorporates owner answers from `Creation_Questions_v2.md`, the analysis in `Creation_Thinking_v3.md`, and the new solution-first validation sequence and per-phase escalation criteria. Open items remaining in `Creation_Questions_v3.md`.*
