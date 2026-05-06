# Implementation Questions — CLI

**Date:** 2026-05-06
**Author:** Build agent
**Purpose:** Open questions surfaced while adding the workshop CLI. None block the build; safe defaults are already applied. Each entry records the default chosen so a reviewer can override before the workshop.

---

## Q1 — Plain-text output format

**Question:** The instruction says "prints to standard out/error" but does not pin down the human-readable shape. The default I shipped is:

```
Topic: <topic>

Synopsis: <synopsis>

Key findings:
  1. <finding>
  ...

Citations:
  [1] <title>
      <url>
      <snippet>
  ...
```

Is this the format the workshop wants on screen during a live demo, or should it be tighter (e.g., findings as `- ` bullets, citations as `[N] <url>` only)?

**Default applied:** the format above. It mirrors how the spec's *Data Model* section reads, which keeps the projected demo output isomorphic with the spec attendees just read.

**How to override:** edit `_format_text` in `agent/cli.py`. The function is ~10 lines and has no callers other than `main`.

---

## Q2 — Should `--json` be the default instead of plain text?

**Question:** The CLI's most likely automation use is piping into `jq` or saving to a file. Plain text is friendlier in a live demo but useless in a script. Is the demo audience the primary user, or is the scripted automation case?

**Default applied:** plain text by default; JSON behind `--json`. Reason: workshop is the primary use case in the instruction; scripts can opt in.

**How to override:** flip the `action` and add a `--text` flag. One-line change.

---

## Q3 — Is a `--stub` flag desirable for offline demos?

**Question:** If the workshop room loses internet, the agent fails on the Tavily call. A `--stub` flag could substitute `StubSearchTool` with a hard-coded result list, letting the demo show CLI ergonomics without a live network. The spec already says "without TAVILY_API_KEY the agent raises NoResultsError" — so today's CLI degrades to an error in the offline case.

**Default applied:** none. Did not add `--stub`. Reason: it would require defining a default stub corpus, which is a teaching surface the spec does not yet cover, and the workshop already has `verify_setup.py` to catch missing-key issues before the session.

**How to override:** add `--stub` and pass a `StubSearchTool(results=…)` into `summarize`. Worth revisiting if internet failures are a recurring workshop pain point.

---

## Q4 — Should the CLI surface the model and temperature in `--help` or in stdout?

**Question:** Pinning the model is itself a teaching point. Today the CLI does not echo which model or temperature was used. An attendee running `python -m agent "X"` cannot see from the output whether the pinned model was honored.

**Default applied:** none — the CLI is silent about model and temperature. Reason: the spec lists these as instructor-only env-var overrides (`SUMMARIZER_MODEL`, `SUMMARIZER_TEMPERATURE`), and exposing them to attendees risks turning a teaching point into a knob.

**How to override:** add a one-line `print(f"# model={model} temperature={t}", file=sys.stderr)` before the API call. Stderr keeps stdout clean for piping.

---

## Q5 — Should the CLI ship with a `console_scripts` entry point?

**Question:** A `pyproject.toml` `console_scripts` entry would let attendees type `research-summarize "topic"` instead of `python -m agent "topic"`. It also requires `pip install -e .` and a `pyproject.toml`, neither of which currently exist in the repo.

**Default applied:** no entry point. `python -m agent` is the documented invocation. Reason: adding `pyproject.toml` is a packaging change with broad implications (build backend, version, project metadata) that is out of scope for "add a simple CLI."

**How to override:** revisit alongside any future packaging work.

---

## Q6 — Should empty stdin or a file argument be supported?

**Question:** Some CLIs accept the topic on stdin (`echo photosynthesis | python -m agent -`) or read from a file. Useful for batch processing.

**Default applied:** positional argument only. Reason: the instruction says "takes topic argument," singular. Adding stdin handling is feature creep against an explicit one-line spec.

**How to override:** add a `nargs="?"` topic with a `sys.stdin.read()` fallback. Trivially small, but should be requested explicitly before adding.
