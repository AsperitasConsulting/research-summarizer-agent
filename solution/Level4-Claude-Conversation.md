# Interaction log with Claude to create level 4 tests

> Initial Prompt
```
I want to write Level 4 tests for this agent as defined in the `Level4` section of the testing pyramid described in file `requirements/Testing-Pyramid.md`. Place the driver for level 4 tests in file `tests/test_level4.py` so that I can independently decide when those tests run. Tests in tests in files `tests/test_level1.py`, `tests/test_level2.py`, and `tests/test_level3.py` are green and need to remain so. Please interview me for any additional information you need. Ask your questions one at a time. Don't write the tests yet until we agree on the plan.
```

> Response

> Epilog

  Exited Claude and executed these commands to make sure that all tests are green: 
  - `python -m pytest tests/test_level1.py -v`
  - `python -m pytest tests/test_level2.py -v`
  - `pytest -m level3 -v`
