# Level 2 — Suggested Claude Code Prompts

These are conversational starters you can paste into Claude Code while writing the two Level 2 tests in `tests/test_level2.py`. Level 2 calls the real Anthropic API, so each test costs quota — use these prompts to think before you run.

---

## 1. Constrained-model end-to-end test

> "I'm trying to write a constrained-model test for the `photosynthesis` topic in `tests/test_level2.py`. The agent needs to be invoked with `temperature=0` and the pinned Haiku model. I see the test file already has `TEST_MODEL` and `TEST_TEMPERATURE` constants and uses `monkeypatch.setenv` — how should I structure the test so it reads cleanly and asserts on the *shape* of the result (counts, presence of fields) rather than exact text the model returns?"

---

## 2. Result-fields-populated test (stubbed search, real model)

> "I want to verify that when I pass pre-built search results into `summarize()` via the `search_tool=` parameter, the resulting `SummaryResult` has all four fields populated. The Anthropic side will be called for real, but I want the search side to be deterministic. How do I structure that, and what assertions are robust without being so loose they'd accept a broken result?"

---

## Optional follow-up

> "Help me think through what additional Level 2 assertions might be worth adding for these tests — without making the tests brittle to model wording variation. Specifically, anything I could check about citation URLs given that `StubSearchTool` knows exactly which URLs went in?"
