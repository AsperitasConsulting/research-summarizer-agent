# Implementation Plan: Research Summarizer Agent

**Version:** 2.0
**Based on:**
- `requirements/Research_Summarizer_Agent_Spec.md` v1.0 draft
- `requirements/Testing-Pyramid.md`
- `notes/Creation_Thinking_v2.md`
- `notes/Creation_Questions_v1.md` (with project-owner answers inline)
**Purpose:** Workshop teaching vehicle for the AI Agent Testing Pyramid (90-minute session)

---

## Guiding Principle

Every decision optimizes for **workshop clarity**, not production quality. If something makes the code harder to understand in 10 minutes, it is wrong. If it makes the workshop run long, it is wrong. The 90-minute clock — with 30–45 minutes of attendee coding inside it — is the benchmark for "is this scoped right?"

---

## Decisions Locked in for v2

| Decision | Choice | Source |
|----------|--------|--------|
| Data model | Pydantic v2 (`>= 2.7, < 3`) | Q7 |
| Structured output | Anthropic native `tool_use` (force tool_choice) | Q8 |
| Intentional defect | Option A (missing `NoResultsError` raise), implemented as a missing code block — obvious by omission | Q12, recommended in spec |
| Solution branch | **Not produced in this build.** Owner builds it later via Claude Code | Q4 |
| `DEFECTS.md` | Not produced now; documented as future deliverable for the solution branch with the fix included | Q4, Q13 |
| Pytest commenting | Extensive — starter files double as pytest tutorials | Q1 |
| Workshop coding budget | 30–45 min → Level 1 = 1 passing test + 3–4 stubs; Level 2 = 1 stub | Q2 |
| Tavily | Required (each attendee brings own free-tier key); `StubSearchTool` for Level 1 | Q3 |
| Anthropic SDK | Latest stable at build time, may re-pin closer to June workshop | Q5 |
| Python | `>=3.11, <3.14` | Q6 |
| Sample outputs | JSON, 2–3 topics | Q9 |
| Level 1 prompts | Prompts attendees paste into Claude Code (not prompts for the agent) | Q10 |
| Eval audience | Instructor-run during Segment 5; attendees can run after the workshop | Q11 |

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
├── tests/
│   ├── __init__.py
│   ├── test_level1.py
│   └── test_level2.py
├── evals/
│   └── judge_eval.py
├── exercises/
│   └── level1_prompts.md
├── sample_outputs/
│   ├── photosynthesis.json
│   └── quantum_computing.json
├── verify_setup.py
├── .env.example
├── requirements.txt
└── README.md
```

> **Note:** No `solution/` directory. Per the answer to Q4, the project owner produces the solution later by working through the workshop with Claude Code.

### 1.2 `requirements.txt`

Top-level pins captured at build time. Initial bounds:

```
anthropic>=X.Y.Z,<NEXT_MAJOR     # latest stable as of build date; record date in README
pydantic>=2.7,<3
tavily-python>=0.5,<1
pytest>=8,<9
python-dotenv>=1,<2
```

The build engineer **must**:
1. Install in a fresh virtualenv to resolve current versions.
2. Run `pip freeze` and replace the placeholder pins above with exact versions.
3. Record the pin date in the README ("Pinned 2026-MM-DD; refresh before workshop date if more than ~30 days old").

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

`pyproject.toml` (or a `python_requires` line in a future `setup.cfg`) declares `>=3.11,<3.14`. If no `pyproject.toml` is created in this build, document the range in the README and `verify_setup.py` enforces the floor at runtime.

---

## Phase 2: Data Model — `agent/models.py`

**Goal:** Define `SummaryResult` and `Citation` using Pydantic v2.

### Tasks

1. `Citation(BaseModel)` — fields: `title: str`, `url: str`, `snippet: str`.
2. `SummaryResult(BaseModel)` — fields: `topic: str`, `synopsis: str`, `key_findings: list[str]`, `citations: list[Citation]`.
3. **No** field validators or constraints — all bounds (synopsis sentence count, findings count, citation URL provenance) are enforced via the prompt only, per spec.
4. Provide a module-level helper `summary_result_tool_schema() -> dict` that returns `SummaryResult.model_json_schema()` shaped for Anthropic tool-use input. Reason: keep schema munging out of `agent.py`.

**Estimated size:** ~30 lines.

**Risk to test in Phase 5:** Pydantic v2 schemas sometimes embed `$defs` that Anthropic tool-use rejects. Build engineer should round-trip the schema once (define tool, force tool use, parse response) before moving on.

---

## Phase 3: Search Tool — `agent/tools.py`

**Goal:** Define the `SearchTool` protocol, both implementations, and the related exceptions.

### Tasks

1. Define `SearchResult` as a Pydantic model — title, url, snippet.
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
3. No conditional logic for empty results — the seeded defect (Phase 5) means this function may receive an empty list, and that is intentional. The function should produce a well-formed but result-less prompt, which becomes the visible symptom in tests.

**Estimated size:** ~40 lines.

---

## Phase 5: Orchestration — `agent/agent.py`

**Goal:** Implement `summarize()` as a five-step pipeline with the seeded defect.

### Tasks

1. Implement `summarize(topic: str, search_tool: SearchTool | None = None) -> SummaryResult`:

   **Step 1 — Validate input**
   - `topic = topic.strip()`
   - `if not topic: raise ValueError("topic must be non-empty")`

   **Step 2 — Execute search**
   - If `search_tool is None`, call `_default_search_tool()`.
   - `results = search_tool.search(topic, max_results=5)`
   - **DEFECT (Option A):** Do NOT check `if not results`. Do NOT raise `NoResultsError`. Allow the empty list to flow into Step 3. No comment marker — the gap is the lesson.

   **Step 3 — Build prompt**
   - `user_message = build_user_message(topic, results)`

   **Step 4 — Call LLM**
   - Read `SUMMARIZER_MODEL` env var (default `"claude-haiku-4-5-20251001"`).
   - Read `SUMMARIZER_TEMPERATURE` env var (default `1.0`, parsed as float).
   - Build a single Anthropic tool from `summary_result_tool_schema()`:
     ```
     tools = [{
         "name": "return_summary",
         "description": "Return the structured research summary.",
         "input_schema": <schema from models.py>,
     }]
     ```
   - Call `client.messages.create(model=..., max_tokens=1024, temperature=..., system=SYSTEM_PROMPT, messages=[{"role": "user", "content": user_message}], tools=tools, tool_choice={"type": "tool", "name": "return_summary"})`.

   **Step 5 — Parse and return**
   - Find the `tool_use` block in `response.content`.
   - Validate via `SummaryResult.model_validate(block.input)`.
   - Return the model instance.
   - Let `anthropic.APIError` and any `pydantic.ValidationError` propagate. (`ValidationError` is rare with `temperature=0` Level 2 tests, but the test suite does not exercise it in this build.)

2. Implement `_default_search_tool()`:
   ```python
   def _default_search_tool() -> SearchTool:
       if os.environ.get("TAVILY_API_KEY"):
           return TavilySearchTool()
       return StubSearchTool(results=[])
   ```

**Estimated size:** ~70 lines.

---

## Phase 6: Package Init — `agent/__init__.py`

**Goal:** Single clean public API surface.

### Tasks

1. `from agent.agent import summarize`
2. `from agent.models import SummaryResult, Citation`
3. `from agent.tools import SearchTool, StubSearchTool, SearchResult, SearchToolError, NoResultsError`
4. Verify `from agent import summarize` works (spec requirement).

**Estimated size:** ~10 lines.

---

## Phase 7: Test Starter Files

**Goal:** Provide well-scaffolded test files that compile, run, double as pytest tutorials, and respect the 30–45 minute coding budget.

### 7.1 `tests/test_level1.py`

Header docstring explains Level 1 testing concepts and the pytest fundamentals attendees will use (fixtures, `pytest.raises`, `monkeypatch` is not needed).

Imports:
- `summarize`, `StubSearchTool`, `SearchResult`, `NoResultsError`, `SearchToolError` from `agent`.

Fixture (commented):
```python
@pytest.fixture
def stub_results():
    """Two pre-built SearchResult objects for use in tests.

    A pytest fixture is a function whose return value is injected into any test
    that names the fixture as a parameter. Use this fixture in your tests by
    adding `stub_results` to the test function's argument list.
    """
    return [
        SearchResult(title="...", url="https://example.com/a", snippet="..."),
        SearchResult(title="...", url="https://example.com/b", snippet="..."),
    ]
```

**One passing test** (uncommented, working from the start — shows attendees the shape of a test):
```python
def test_empty_topic_raises_value_error():
    """summarize('') must reject the empty topic before doing anything else."""
    with pytest.raises(ValueError):
        summarize("")
```

**Three commented stubs** (exact count = 4 tests total in this file):

1. `test_no_results_raises_no_results_error` — inject `StubSearchTool(results=[])`, expect `NoResultsError`. **This is the test that surfaces the seeded defect.**
2. `test_search_tool_error_propagates` — inject a stub whose `.search()` raises `SearchToolError`; expect it to propagate.
3. `test_result_fields_populated` — inject `stub_results`, call `summarize()`, assert `result.topic`, `result.synopsis`, `result.key_findings`, and `result.citations` are present and non-empty. (This test does call the real Anthropic API since the search step is stubbed but the LLM step is not — note this in the comment so attendees know it requires `ANTHROPIC_API_KEY`. If we want a strictly Level 1 version, mock the Anthropic client; for the workshop's purposes, the simpler version is fine and matches the spec's scope.)

> Decision point during build: if Phase 7 reviewers feel test #3 muddies the Level 1 boundary, replace it with a purely structural test (e.g., assert `summarize()` calls `search_tool.search()` exactly once via a custom recording stub). Defer to the build engineer's judgment when the file is written.

Each commented stub uses Arrange/Act/Assert structure to teach the pattern:
```python
# def test_no_results_raises_no_results_error(stub_results):
#     # Arrange: build a StubSearchTool with an empty results list
#     # Act: call summarize() with that tool
#     # Assert: pytest.raises(NoResultsError) wraps the call
#     pass
```

**Estimated size:** ~80 lines including comments.

### 7.2 `tests/test_level2.py`

Header docstring explains Level 2 testing concepts (real model calls, `temperature=0`, structured output verification) and **why model pinning matters** — workshop teaching point.

Constants at top:
```python
TEST_MODEL = "claude-haiku-4-5-20251001"
TEST_TEMPERATURE = 0
```

Module-level skip guard:
```python
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Level 2 tests require ANTHROPIC_API_KEY and TAVILY_API_KEY",
)
```

**One stub test** (commented):
```python
# def test_photosynthesis_summary(monkeypatch):
#     """Constrained-model test: real Anthropic + real Tavily, deterministic config.
#
#     We pin the model and force temperature=0 so we get the lowest-variance
#     response we can. Even so, this test asserts on shape, not specific text.
#     """
#     # Arrange: monkeypatch SUMMARIZER_MODEL and SUMMARIZER_TEMPERATURE so the
#     # agent uses the test pins regardless of what the env says.
#     # Act: call summarize("photosynthesis")
#     # Assert:
#     #   - len(result.key_findings) >= 2
#     #   - len(result.citations) >= 1
#     pass
```

**Estimated size:** ~60 lines including comments.

---

## Phase 8: Evals — `evals/judge_eval.py`

**Goal:** Pre-built LLM-as-judge demo for workshop Segment 5; instructor-run during the workshop, attendee-runnable afterwards.

### Tasks

1. **Topic and run loop:** Hard-code a topic the agent generally handles well (e.g., "the discovery of penicillin"). Single run, not a sweep — the demo needs to fit ~15 minutes including discussion.
2. **Judge model:** `claude-sonnet-4-6` (different from the agent's Haiku, illustrating actor/judge separation). Pin in a constant at the top.
3. **Rubric (pass/fail per dimension, total score = sum of passes / dimensions):**
   - **Factual accuracy:** Synopsis and key findings are consistent with each other and with the cited snippets.
   - **Citation integrity:** Every cited URL appears in the search-tool output passed to the agent. (This is the hallucination check; the judge gets the original search results in its prompt.)
   - **Synopsis quality:** 2–4 sentences, on-topic, no opinions/recommendations.
   - **Findings count:** 2–5 findings, each is 1–2 sentences and substantive.
4. **Output:** Print the agent result, the judge's prompt (in a foldable section if running in a TTY that supports it; otherwise just a labelled block), the judge's verdict per dimension, and the overall score.
5. **Comments:** Each rubric dimension explained inline, so attendees who run the eval after the workshop can read the file and learn the rubric pattern.
6. **No caching, no flags expected.** Idempotent: running `python evals/judge_eval.py` from the repo root with both API keys set just works.

**Estimated size:** ~140 lines including comments.

---

## Phase 9: Exercises — `exercises/level1_prompts.md`

**Goal:** Suggested prompts attendees paste into Claude Code while writing Level 1 tests.

### Tasks

1. **4–6 prompts**, mapped 1:1 to the Level 1 stub tests:
   - "Help me write a pytest test that verifies `summarize('')` raises `ValueError`. Use the existing `StubSearchTool` so no real API calls are made."
   - "I need a test that exercises what happens when `StubSearchTool` returns an empty list. The test should expect `NoResultsError` to be raised."
   - "Write a test that injects a `StubSearchTool` whose `search()` method raises `SearchToolError`. The test should verify the exception propagates out of `summarize()`."
   - "Help me write a test that calls `summarize()` with the `stub_results` fixture and asserts that the returned `SummaryResult` has all four fields populated and non-empty."
   - (Optional 5th/6th prompts for fast attendees — e.g., parametrize the empty-topic test for whitespace inputs, or add a recording stub that asserts `search()` was called exactly once.)
2. Each prompt is **a natural-language instruction**, not a question. Direct imperative voice — workshop velocity matters.
3. Do **not** include the answer code in this file. Show only the prompt.

---

## Phase 10: Sample Outputs — `sample_outputs/`

**Goal:** Concrete examples of `SummaryResult` shape and quality.

### Tasks

1. `photosynthesis.json` — simple, factual topic. 3 key findings, 3 citations.
2. `quantum_computing.json` — technical, multi-perspective topic. 4 key findings, 4 citations.
3. (Optional) `espresso_brewing.json` for a third variety topic.
4. Each file is a hand-curated, valid `SummaryResult` JSON serialization.
5. **Citation URLs:** Use clearly synthetic `https://example.com/...` URLs to avoid linkrot before June. Mark this convention in a one-line comment in the README so attendees do not expect live URLs.

---

## Phase 11: Verify Setup — `verify_setup.py`

**Goal:** Pre-workshop self-check that fails loudly with actionable messages.

### Checks (in order, all printed with PASS/FAIL prefixes)

1. Python version `>= 3.11` and `< 3.14`.
2. All packages in `requirements.txt` import cleanly (`anthropic`, `pydantic`, `tavily`, `pytest`, `dotenv`).
3. `ANTHROPIC_API_KEY` is set and non-empty.
4. Minimal Anthropic API call (single-token completion) succeeds.
5. `TAVILY_API_KEY` presence — print PASS if set, WARN (not FAIL) if absent. Do **not** make a Tavily call by default (avoids burning the attendee's free-tier quota on every setup run).

### Behavior

- Exit code `0` on full pass (all PASS, optional WARN allowed).
- Exit code `1` on any FAIL.
- Each FAIL must include a remediation hint (e.g., "FAIL: ANTHROPIC_API_KEY not set. Add it to your .env file or export it: `export ANTHROPIC_API_KEY=sk-ant-...`").
- Output is plain text suitable for screen-sharing.

**Estimated size:** ~100 lines.

---

## Phase 12: Documentation — `README.md`

**Goal:** Single onboarding doc for attendees and instructors.

### Sections (recommended order)

1. **What this is** — single paragraph: workshop teaching vehicle, not production.
2. **Prereqs** — Python 3.11–3.13, Anthropic key with billing, Tavily free-tier key. Linkable signup steps.
3. **Setup** — `python -m venv`, activate, `pip install -r requirements.txt`, copy `.env.example` to `.env`, fill in keys, `python verify_setup.py`.
4. **How the agent works** — link to `requirements/Research_Summarizer_Agent_Spec.md`. Two-paragraph summary inline.
5. **Running tests** — `pytest tests/test_level1.py` (no API key needed for the passing test), `pytest tests/test_level2.py` (needs Anthropic + Tavily keys).
6. **Running the eval** — `python evals/judge_eval.py`.
7. **Design choices** — Pydantic v2 + native tool_use rationale. Pin date and refresh playbook.
8. **Sample output URL convention** — synthetic `example.com` URLs, why.
9. **Troubleshooting** — common failures from `verify_setup.py` mapped to fixes.

**Note:** No `DEFECTS.md` in this build. The plan documents that the project owner will create it on the solution branch later, including the 2-line fix:
```python
if not results:
    raise NoResultsError(topic)
```

---

## Implementation Order

| Order | Phase | Depends On | Why this order |
|-------|-------|------------|----------------|
| 1 | Scaffolding | — | Everything needs the directories and pinned deps |
| 2 | Models | 1 | Types are referenced by tools, prompts, agent, eval |
| 3 | Tools | 2 | Uses `SearchResult` + defines exceptions |
| 4 | Prompts | 2, 3 | Formats `SearchResult` lists into messages |
| 5 | Agent | 2–4 | Wires everything; the seeded defect lives here |
| 6 | Package init | 5 | Re-exports from completed modules |
| 7 | Test starters | 6 | Need `from agent import ...` to work |
| 8 | Evals | 6 | Calls `summarize()`; uses Sonnet judge |
| 9 | Exercises | 7 | Mirrors test stubs |
| 10 | Sample outputs | 2 | Just JSON serializations of `SummaryResult` |
| 11 | Verify setup | 1 | Standalone script; depends only on installed deps |
| 12 | README | All | Describes the finished project |

---

## Intentional Defect Plan

**Chosen:** Option A — `summarize()` does not raise `NoResultsError` on empty search results.

**Implementation:** In `agent/agent.py`, omit the empty-results guard between `search_tool.search(...)` and `build_user_message(...)`. No comment marker. No TODO. Just the missing block.

**Why this implementation style:**
- Mixed-skill audience (per Q12 answer: "obvious") — a missing block is more obvious than a buggy block to a beginner.
- A reader who scans the spec's exception table sees `NoResultsError` listed, then sees no place where it is raised — that is the discovery moment.
- Level 1 test #1 (`test_no_results_raises_no_results_error`) catches it deterministically with no API key needed.

**Fix (for the future solution branch):**
```python
results = search_tool.search(topic, max_results=5)
if not results:
    raise NoResultsError(topic)
```

**`DEFECTS.md` contents (for solution branch — not built now):**
- Which option (A) was chosen.
- Why (workshop pedagogy, deterministic Level 1 catchability).
- Exact diff applied to fix it.

---

## Verification Criteria

Before declaring the build complete:

- [ ] `python verify_setup.py` exits 0 with all keys present, exits 1 if Anthropic key missing.
- [ ] `pytest tests/test_level1.py` runs cleanly: 1 test passes (`test_empty_topic_raises_value_error`); commented stubs are skipped/ignored, not errors.
- [ ] `pytest tests/test_level2.py` skips cleanly when `ANTHROPIC_API_KEY` is unset.
- [ ] `pytest tests/test_level2.py` runs the photosynthesis stub successfully when keys are present (after attendees uncomment it).
- [ ] `from agent import summarize, SummaryResult` works.
- [ ] A live `summarize("photosynthesis")` returns a valid `SummaryResult` with non-empty fields.
- [ ] `python evals/judge_eval.py` produces readable output with a per-dimension verdict.
- [ ] Every `agent/*.py` file is under 100 lines (well under the 500-line CLAUDE.md ceiling).
- [ ] No secrets in committed code; `.env.example` documents every variable.
- [ ] Pin date recorded in README; pin-refresh command documented.
- [ ] No `solution/` directory; no `DEFECTS.md` in this build.

---

## Out of Scope (Reaffirmed from Spec)

- Multi-turn conversation, session state, memory.
- Caching, deduplication, retry/backoff, rate limiting.
- Streaming.
- UI / CLI beyond `verify_setup.py`.
- Logging frameworks (print is fine).
- Auth beyond env-var API keys.

---

*Document version: 2.0 — incorporates project-owner answers from `Creation_Questions_v1.md` and the analysis in `Creation_Thinking_v2.md`. Open items remaining in `Creation_Questions_v2.md`.*
