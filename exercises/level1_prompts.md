# Level 1 — Suggested Claude Code Prompts

These are conversational starters you can paste into Claude Code while writing the three Level 1 tests in `tests/test_level1.py`. They mirror the three tests one-for-one. Use them as a kick-off; refine as you go.

---

## 1. Empty-topic test (already written, for reference)

> "I'm looking at `tests/test_level1.py`. The first test, `test_empty_topic_raises_value_error`, is already written and passing — can you walk me through what it's doing? I want to use it as the model for my own tests."

---

## 2. No-results test (defect-catching)

> "I want to verify that when the search tool returns no results, `summarize()` raises `NoResultsError`. There's a `# TODO: handle empty results` marker in `agent/agent.py` near the relevant code path that hints at where the gap is. How would I set up a `StubSearchTool` with an empty list to make that happen, and what's the right way to assert the exception with `pytest.raises`?"

---

## 3. Tool-error propagation test

> "Could you help me write a test where the search tool itself raises `SearchToolError` from inside `.search()`, and we want to confirm `summarize()` lets that exception propagate? I think I'll need a tiny custom class instead of `StubSearchTool` — does any object with a `.search(query, max_results)` method count as a `SearchTool`?"

---

## Optional follow-ups

> "Can you parametrize the empty-topic test to also cover whitespace-only inputs like `'   '` and `'\t'`?"

> "I want a 'recording stub' that captures whatever query and max_results the agent passes in, so I can assert on the call. Can you sketch that?"
