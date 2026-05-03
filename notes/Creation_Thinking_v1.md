# Creation Thinking v1

## Analysis of Requirements

### Core Nature of the Project

This is **not** a production agent. It is a **workshop teaching vehicle** for the AI Agent Testing Pyramid. Every design decision must be evaluated through the lens of: "Can a workshop attendee understand this in under 10 minutes?" This constraint is the most important thing in the spec and should govern all implementation choices.

### What the Agent Actually Does

The agent is a single-function pipeline:

```
topic string → validate → search → build prompt → call LLM → parse → SummaryResult
```

There are no branches, no retries, no state, no conversation history. It's essentially a function with five sequential steps. This simplicity is intentional and must be preserved.

### Key Design Decisions to Make

**1. Pydantic vs Dataclass**

The spec leaves this open. Pydantic is recommended in the spec itself because it enables automatic validation, which is useful for structured output parsing from the LLM. Since the agent uses `claude-haiku-4-5-20251001` with structured output, Pydantic is the natural choice — the Anthropic SDK's structured output feature works well with Pydantic models. Dataclasses would require manual parsing logic that adds complexity without teaching value.

**Decision: Use Pydantic.** Rationale: less parsing code, automatic validation, better structured output support with the Anthropic SDK.

**2. Which Intentional Defect**

The spec recommends Option A: agent doesn't raise `NoResultsError` on empty search results. This is the right choice because:
- It's deterministic (no model variability)
- It fails fast in Level 1 tests (no API keys needed)
- It's satisfying to discover and fix
- It teaches that even simple orchestration logic needs testing

**Decision: Option A** (NoResultsError not raised on empty results).

**3. Structured Output Approach**

The Anthropic SDK supports tool use / function calling for structured output. With Pydantic models, we can use the SDK's built-in support to request responses matching the `SummaryResult` schema. This avoids manual JSON parsing.

**4. Dependency Injection Pattern**

The `summarize()` function accepts an optional `search_tool` parameter. When `None`, it selects based on environment variables. This is a clean pattern that:
- Makes Level 1 tests trivial (inject `StubSearchTool`)
- Avoids monkeypatching
- Is easy to explain in a workshop

### Architecture Observations

**Separation of concerns is clear and minimal:**
- `models.py` — data types only (Pydantic models)
- `tools.py` — search tool protocol + implementations (Tavily + Stub)
- `prompts.py` — prompt text construction
- `agent.py` — orchestration + `summarize()` entry point
- `__init__.py` — re-exports `summarize` and `SummaryResult`

Each file has a single responsibility. None should exceed ~100 lines. This is good for a workshop — attendees can hold the entire codebase in their head.

**Error hierarchy is flat:**
- `ValueError` (stdlib)
- `SearchToolError` (custom)
- `NoResultsError` (custom)
- `anthropic.APIError` (passthrough)

No retry logic, no error wrapping, no recovery. Errors propagate immediately. This makes test assertions simple and predictable.

### Testing Surface Area

**Level 1 (Deterministic, mocked):**
- Input validation (empty topic → ValueError)
- Empty search results → NoResultsError (this is the intentional defect!)
- Search tool failure → SearchToolError propagation
- Result field mapping (topic echoed, findings present, citations present)
- All use StubSearchTool — no API keys needed, sub-second execution

**Level 2 (Real model, constrained):**
- Real Anthropic API call with temperature=0
- Schema compliance (structured output returns valid SummaryResult)
- Key findings count within bounds
- Citations present and non-empty
- Requires ANTHROPIC_API_KEY (skip guard when absent)

**Level 3 (LLM-as-judge, pre-built demo):**
- Semantic quality of summaries
- Citation integrity (URLs from search results only)
- Hallucination detection
- This is pre-built for the workshop, not written by attendees

### Workshop Flow Considerations

The test starter files are critical. They must:
1. Import cleanly
2. Run without errors (stubs fail with clear assertion messages, not import errors)
3. Include one passing test as an example
4. Have enough scaffolding that attendees write test logic, not boilerplate

The `verify_setup.py` script gates the workshop start. If it fails, the attendee is stuck. It must be robust and give actionable error messages.

### Risk Areas

1. **Anthropic SDK version sensitivity** — Structured output API may vary across SDK versions. Pin the SDK version in `requirements.txt`.
2. **Tavily API availability** — If Tavily is down during the workshop, Level 2 tests with real search fail. The stub fallback mitigates this for Level 1, but Level 2 tests that call real search will need Tavily.
3. **Model availability** — `claude-haiku-4-5-20251001` must be available. If Anthropic deprecates it before the workshop, tests break silently.
4. **Structured output format** — The LLM might not perfectly follow the schema every time. Temperature=0 for Level 2 tests mitigates this but doesn't eliminate it.
