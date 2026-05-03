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
call. The marker comment `# TODO: handle empty results` is the only hint in the
source.

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

- Phase 8 run (corrected agent): all 5 tests pass.
- Phase 9 run (defective agent): only
  `test_no_results_raises_no_results_error` fails; the other 4 pass.

### Phase 8 — Corrected agent (`pytest solution/tests/ -v`)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.2, pluggy-1.6.0 -- /home/derek/git/personal/agents/research-summarizer-agent/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/derek/git/personal/agents/research-summarizer-agent
plugins: anyio-4.13.0
collected 5 items

solution/tests/test_level1.py::test_empty_topic_raises_value_error PASSED [ 20%]
solution/tests/test_level1.py::test_no_results_raises_no_results_error PASSED [ 40%]
solution/tests/test_level1.py::test_search_tool_error_propagates PASSED  [ 60%]
solution/tests/test_level2.py::test_photosynthesis_summary PASSED        [ 80%]
solution/tests/test_level2.py::test_result_fields_populated PASSED       [100%]

============================== 5 passed in 6.67s ===============================
```

### Phase 9 — Defective agent, Level 1 (`pytest solution/tests/test_level1.py -v`)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.2, pluggy-1.6.0 -- /home/derek/git/personal/agents/research-summarizer-agent/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/derek/git/personal/agents/research-summarizer-agent
plugins: anyio-4.13.0
collected 3 items

solution/tests/test_level1.py::test_empty_topic_raises_value_error PASSED [ 33%]
solution/tests/test_level1.py::test_no_results_raises_no_results_error FAILED [ 66%]
solution/tests/test_level1.py::test_search_tool_error_propagates PASSED  [100%]

=================================== FAILURES ===================================
___________________ test_no_results_raises_no_results_error ____________________

    def test_no_results_raises_no_results_error() -> None:
        empty_tool = StubSearchTool(results=[])
>       with pytest.raises(NoResultsError):
E       Failed: DID NOT RAISE <class 'agent.tools.NoResultsError'>

solution/tests/test_level1.py:48: Failed
=========================== short test summary info ============================
FAILED solution/tests/test_level1.py::test_no_results_raises_no_results_error
========================= 1 failed, 2 passed in 1.89s ==========================
```

### Phase 9 — Defective agent, Level 2 (`pytest solution/tests/test_level2.py -v`)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.2, pluggy-1.6.0 -- /home/derek/git/personal/agents/research-summarizer-agent/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/derek/git/personal/agents/research-summarizer-agent
plugins: anyio-4.13.0
collected 2 items

solution/tests/test_level2.py::test_photosynthesis_summary PASSED        [ 50%]
solution/tests/test_level2.py::test_result_fields_populated PASSED       [100%]

============================== 2 passed in 7.19s ===============================
```
