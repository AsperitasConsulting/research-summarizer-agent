# Implementation Plan: Research Summarizer Agent

**Version:** 1.0
**Based on:** `requirements/Research_Summarizer_Agent_Spec.md` v1.0 draft
**Purpose:** Workshop teaching vehicle for the AI Agent Testing Pyramid

---

## Guiding Principle

Every decision optimizes for **workshop clarity**, not production quality. If something makes the code harder to understand in 10 minutes, it's wrong.

---

## Phase 1: Project Scaffolding

**Goal:** Establish the file structure and dependency baseline so everything imports cleanly from day one.

### Tasks

1. **Create directory structure**
   ```
   agent/
   ├── __init__.py
   ├── agent.py
   ├── tools.py
   ├── models.py
   └── prompts.py
   tests/
   ├── __init__.py
   ├── test_level1.py
   └── test_level2.py
   evals/
   └── judge_eval.py
   exercises/
   └── level1_prompts.md
   sample_outputs/
   solution/
   ```

2. **Create `requirements.txt`** with pinned versions:
   ```
   anthropic>=0.52.0,<1.0.0
   pydantic>=2.0.0,<3.0.0
   tavily-python>=0.5.0,<1.0.0
   pytest>=8.0.0,<9.0.0
   python-dotenv>=1.0.0,<2.0.0
   ```
   Note: Exact version pins TBD based on answers to questions in `notes/Creation_Questions_v1.md`.

3. **Create `.env.example`**
   ```
   ANTHROPIC_API_KEY=your-key-here
   TAVILY_API_KEY=your-key-here
   # SUMMARIZER_MODEL=claude-haiku-4-5-20251001
   # SUMMARIZER_TEMPERATURE=1.0
   ```

4. **Create `verify_setup.py`** at the project root (spec requirement).

---

## Phase 2: Data Model (`agent/models.py`)

**Goal:** Define `SummaryResult` and `Citation` using Pydantic v2.

### Design Decision
- **Pydantic over dataclass.** Rationale: automatic validation, native structured output support with the Anthropic SDK, less manual parsing code.

### Tasks

1. Define `Citation(BaseModel)` with fields: `title: str`, `url: str`, `snippet: str`
2. Define `SummaryResult(BaseModel)` with fields: `topic: str`, `synopsis: str`, `key_findings: list[str]`, `citations: list[Citation]`
3. No field-level validators — constraints are enforced via prompt, not code (per spec)

### Estimated size: ~25 lines

---

## Phase 3: Search Tool Interface (`agent/tools.py`)

**Goal:** Define the `SearchTool` protocol and both implementations.

### Tasks

1. Define `SearchResult` as a Pydantic model or simple dataclass (title, url, snippet)
2. Define `SearchToolError` exception class
3. Define `NoResultsError` exception class
4. Define `SearchTool` protocol with `search(query: str, max_results: int = 5) -> list[SearchResult]`
5. Implement `TavilySearchTool`:
   - Uses `tavily-python` client
   - Reads `TAVILY_API_KEY` from environment
   - 10-second timeout
   - Wraps Tavily errors in `SearchToolError`
   - Returns empty list (not exception) for zero results
6. Implement `StubSearchTool`:
   - Accepts `results: list[SearchResult]` at construction
   - Returns pre-configured list regardless of query
   - Importable as `from agent.tools import StubSearchTool`

### Estimated size: ~80 lines

---

## Phase 4: Prompts (`agent/prompts.py`)

**Goal:** Isolate prompt text so it's easy to read, test, and modify.

### Tasks

1. Define `SYSTEM_PROMPT` constant (exact text from spec)
2. Define `build_user_message(topic: str, results: list[SearchResult]) -> str` function
   - Formats topic and search results per the spec's user message template
   - Each result formatted as `[{index}] {title}\nURL: {url}\n{snippet}\n`

### Estimated size: ~40 lines

---

## Phase 5: Orchestration (`agent/agent.py`)

**Goal:** Implement the `summarize()` function with the five-step pipeline.

### Tasks

1. Implement `summarize(topic: str, search_tool: SearchTool | None = None) -> SummaryResult`:

   **Step 1 — Validate input:**
   - Strip whitespace from topic
   - Raise `ValueError` if empty

   **Step 2 — Execute search:**
   - If `search_tool` is None, select based on environment (Tavily if key present, else Stub with empty list)
   - Call `search_tool.search(topic, max_results=5)`
   - **INTENTIONAL DEFECT (Option A):** Do NOT check for empty results. Do NOT raise `NoResultsError`. Pass the empty list through to prompt building. This is the seeded bug that Level 1 tests should catch.

   **Step 3 — Build prompt:**
   - Call `build_user_message(topic, results)`

   **Step 4 — Call LLM:**
   - Read model from `SUMMARIZER_MODEL` env var, default `claude-haiku-4-5-20251001`
   - Read temperature from `SUMMARIZER_TEMPERATURE` env var, default `1.0`
   - Use Anthropic SDK with structured output to request `SummaryResult`
   - `max_tokens=1024`

   **Step 5 — Return:**
   - Return the parsed `SummaryResult`
   - Let `anthropic.APIError` propagate naturally

2. Implement tool selection helper (private function):
   ```python
   def _default_search_tool() -> SearchTool:
       if os.environ.get("TAVILY_API_KEY"):
           return TavilySearchTool()
       return StubSearchTool(results=[])
   ```

### Estimated size: ~60 lines

---

## Phase 6: Package Init (`agent/__init__.py`)

**Goal:** Clean public API surface.

### Tasks

1. Re-export `summarize` from `agent.py`
2. Re-export `SummaryResult` and `Citation` from `models.py`
3. Ensure `from agent import summarize` works per spec

### Estimated size: ~5 lines

---

## Phase 7: Test Starter Files

**Goal:** Provide well-scaffolded test files that compile, run, and guide attendees.

### `tests/test_level1.py`

1. Imports: `summarize`, `StubSearchTool`, `SearchResult`, `NoResultsError`, `SearchToolError`
2. `stub_results` fixture: returns 2 pre-built `SearchResult` objects with realistic data
3. **Passing test:** `test_empty_topic_raises_value_error` — asserts `summarize("")` raises `ValueError`
4. **Commented stubs:**
   - `test_no_results_raises_no_results_error` — inject stub with empty list
   - `test_search_tool_error_propagates` — inject a stub that raises `SearchToolError`
   - `test_result_fields_populated` — inject stub, call summarize, assert fields on `SummaryResult`

### `tests/test_level2.py`

1. Constants at top: `TEST_MODEL = "claude-haiku-4-5-20251001"`, `TEST_TEMPERATURE = 0`
2. Skip guard: skip entire module if `ANTHROPIC_API_KEY` not set
3. Comment explaining why model is pinned and temperature is zero
4. **Stub test:** `test_photosynthesis_summary` — call `summarize("photosynthesis")`, assert `len(result.key_findings) >= 2` and `len(result.citations) >= 1`

### Estimated size: ~50 lines each

---

## Phase 8: Evals (`evals/judge_eval.py`)

**Goal:** Pre-built LLM-as-judge demo for workshop Segment 5.

### Tasks

1. Implement a function that:
   - Calls `summarize()` for a test topic
   - Sends the result to a judge LLM (Claude Sonnet or Opus) with a rubric
   - Rubric checks: factual accuracy, citation integrity (URLs from search results only), synopsis quality, findings count
2. Print a structured verdict (pass/fail per rubric dimension + overall score)
3. This is a **demo**, not attendee-written code — it should be polished and well-commented

### Estimated size: ~80 lines

---

## Phase 9: Exercises (`exercises/level1_prompts.md`)

**Goal:** Provide suggested Claude Code prompts that guide attendees through writing Level 1 tests.

### Tasks

1. Write 4-6 prompts, each targeting a specific test case:
   - "Write a test that verifies summarize raises ValueError for whitespace-only input"
   - "Write a test that checks what happens when the search tool returns no results"
   - "Write a test that verifies SearchToolError propagates correctly"
   - "Write a test that checks all SummaryResult fields are populated correctly"
2. Each prompt should be a natural-language instruction an attendee could paste into Claude Code
3. Do not include the answer — just the prompt

---

## Phase 10: Sample Outputs (`sample_outputs/`)

**Goal:** Give attendees concrete examples of what `SummaryResult` looks like.

### Tasks

1. Create 2-3 JSON files with realistic `SummaryResult` examples:
   - `photosynthesis.json` — standard topic
   - `quantum_computing.json` — technical topic
2. Each file is a serialized `SummaryResult` with realistic citations

---

## Phase 11: Verify Setup Script (`verify_setup.py`)

**Goal:** Pre-workshop environment self-check.

### Tasks

1. Check Python version >= 3.11
2. Check all packages in `requirements.txt` are importable
3. Check `ANTHROPIC_API_KEY` is set and non-empty
4. Make a minimal Anthropic API call (single-token completion)
5. Check `TAVILY_API_KEY` presence (warn if absent, don't fail)
6. Print clear pass/fail per check with actionable error messages
7. Exit code 0 on full pass, 1 on any failure

### Estimated size: ~60 lines

---

## Phase 12: Documentation

### Tasks

1. **`README.md`** — Setup instructions, workshop overview, how to run tests, how to run verify_setup.py. Document the Pydantic choice and rationale.
2. **`DEFECTS.md`** — Document that Option A was chosen. Commit only to the `solution` branch.

---

## Implementation Order

The phases above are sequenced for incremental buildability:

| Order | Phase | Depends On | Rationale |
|-------|-------|------------|-----------|
| 1 | Scaffolding | — | Everything needs directories and deps |
| 2 | Data Model | Phase 1 | Types are referenced everywhere |
| 3 | Search Tools | Phase 2 | Uses SearchResult type |
| 4 | Prompts | Phases 2, 3 | Uses SearchResult for formatting |
| 5 | Orchestration | Phases 2-4 | Ties everything together |
| 6 | Package Init | Phase 5 | Re-exports from completed modules |
| 7 | Test Starters | Phase 6 | Need working imports to compile |
| 8 | Evals | Phase 6 | Calls summarize() |
| 9 | Exercises | Phase 7 | References test file structure |
| 10 | Sample Outputs | Phase 2 | Just serialized models |
| 11 | Verify Setup | Phase 1 | Standalone script |
| 12 | Documentation | All | Describes the completed project |

---

## Intentional Defect Plan

**Chosen option:** A — Agent does not raise `NoResultsError` when search returns empty list.

**Implementation:** In `agent.py`, omit the empty-result check after `search_tool.search()`. The search results (empty list) pass directly to `build_user_message()`, which formats zero results. The LLM receives a prompt with no search data and returns a `SummaryResult` with potentially hallucinated content or empty fields.

**Why this is good for teaching:**
- Level 1 test with `StubSearchTool(results=[])` catches it immediately
- No API keys needed to demonstrate the bug
- Fix is a 2-line `if not results: raise NoResultsError(topic)` — easy to understand
- Demonstrates that orchestration logic (not just the LLM) needs testing

**Where the fix lives:** `solution` branch, documented in `DEFECTS.md`.

---

## Verification Criteria

Before declaring the implementation complete:

- [ ] `python verify_setup.py` passes all checks (with API keys)
- [ ] `pytest tests/test_level1.py` runs — the one non-stub test passes, stubs are skipped/commented
- [ ] `pytest tests/test_level2.py` runs — skips cleanly without `ANTHROPIC_API_KEY`
- [ ] `pytest tests/test_level2.py` runs with API key — stub test passes
- [ ] `from agent import summarize, SummaryResult` works
- [ ] `summarize("photosynthesis")` returns a valid `SummaryResult` (with API keys)
- [ ] No file exceeds 500 lines
- [ ] No secrets in committed code
- [ ] `.env.example` has all required variables documented
