# Implementation Thinking — CLI

**Date:** 2026-05-06
**Author:** Build agent
**Purpose:** Document reasoning behind adding a small workshop CLI on top of the existing `summarize()` entry point.

---

## Scope and constraint

The workshop instruction is one sentence: a CLI that takes a topic argument and prints to stdout/stderr. The agent itself is already done, well under 250 lines, and the spec's "10-minute comprehension" rule still applies. The CLI must be a thin wrapper — anything that adds shape to the agent's behavior (retries, formatting choices the model didn't make, etc.) belongs in `agent/`, not the CLI.

The current spec lists "Any UI or CLI beyond what `verify_setup.py` requires" under Out of Scope. That line predates this instruction and must be amended; the spec is now the single source of truth for the CLI surface.

## Module placement

Three reasonable options:

1. `cli.py` at repo root.
2. `agent/cli.py` (importable as `python -m agent.cli`).
3. `agent/__main__.py` (so `python -m agent` works directly).

Picked **option 3 with option 2 as the implementation**: put logic in `agent/cli.py` and have `agent/__main__.py` re-export `main()`. Reasons:

- `python -m agent "topic"` is the shortest invocation a workshop attendee can type that does not require `pip install -e .` or a console-script entry point. Setuptools entry points add a packaging step that is itself a distraction from the testing curriculum.
- Keeping the implementation in `agent/cli.py` rather than `__main__.py` means it can be unit-tested without `runpy`. The workshop does not require CLI tests, but leaving the door open is cheap.
- Repo-root `cli.py` was rejected: it pollutes import paths and breaks the package boundary the rest of the code respects.

## Argument shape

A single positional `topic` argument. No subcommands. One optional `--json` flag for machine-readable output (useful when an attendee wants to pipe into `jq`); plain text is the default because the workshop demos run live and humans need to read it.

Rejected: flags for model, temperature, max-tokens. Those are already configurable via environment variables (`SUMMARIZER_MODEL`, `SUMMARIZER_TEMPERATURE`) per the spec. Adding CLI flags would be a second configuration surface, and the spec is explicit that environment variables are the configuration mechanism.

Rejected: a `--quiet` flag. The CLI never logs to stdout other than the result, so there is nothing to silence. Errors go to stderr. The output is already pipe-friendly.

## Output format

**stdout** — the result. Plain-text by default:

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

When `--json` is passed, stdout receives `SummaryResult.model_dump_json(indent=2)` and nothing else. This is straight Pydantic; no hand-rolled serialization.

**stderr** — error class name and message on a single line, prefixed with `error:` for greppability. Examples:

- `error: ValueError: topic must be non-empty`
- `error: NoResultsError: search returned no results`
- `error: SearchToolError: Tavily search failed: ...`
- `error: anthropic.APIError: ...`

## Exit codes

The spec already enumerates the four exception types `summarize()` can raise. I considered mapping each to a distinct non-zero exit code, but rejected that:

- The workshop never asserts on specific exit codes.
- A four-way taxonomy invites attendees to write tests against it, which is out of scope.
- POSIX convention is "0 success, non-zero failure" — anything finer is an additional contract to maintain.

So: **0 on success, 1 on any handled error, 2 on argparse usage error** (argparse's default for `--help` / missing arg). That is the minimum viable contract.

## Error handling philosophy

The CLI catches `ValueError`, `NoResultsError`, `SearchToolError`, and `anthropic.APIError` only — exactly the four exceptions the spec documents `summarize()` as raising. Anything else propagates as an uncaught traceback. Reason: an unexpected exception in the CLI usually means a bug in the agent, and a traceback is the right diagnostic output for that case. Catching `Exception` would hide bugs from workshop attendees.

I am not importing `anthropic` in the CLI module just to reference `anthropic.APIError` — instead, the `except` clause uses a duck-typed check (`isinstance(exc, anthropic.APIError)` after a single import) so the import surface stays narrow. Re-evaluated: cleaner to import `anthropic` once at module top. The agent already depends on it transitively; importing it in the CLI is honest.

## What the CLI does NOT do

- No retry on transient API errors. The spec is explicit: no retry logic anywhere. The CLI inherits that.
- No caching. Same reason.
- No streaming. The agent returns a single `SummaryResult`; there is nothing to stream.
- No `.env` loading. `agent.agent` already calls `load_dotenv()` at import time, so the CLI gets that for free. Adding a second `load_dotenv()` would be redundant.
- No verbose / debug flag. If an attendee needs diagnostics, they can read the agent source.

## Documentation footprint

- `README.md`: add a "Running the CLI" section after "How the agent works" and before "Running tests". One example invocation, one mention of `--json`, one mention of exit codes.
- `requirements/Research_Summarizer_Agent_Spec.md`:
  - Remove the CLI exclusion from "Out of Scope".
  - Add a new "Command-Line Interface" section between "Configuration" and "Test Starter Files" that mirrors the contract the implementation honors (entry point, args, output, exit codes).

The spec change is bigger than the README change because the spec is the contract. Future build agents reading the spec must see the CLI as part of the agent's documented surface, not as an undocumented script.

## Testing

Out of scope per the instruction (the task says "document how to run", not "test"). The CLI is small enough that a future addition of a `test_cli.py` would be straightforward — it would invoke `agent.cli.main([...])` with a `StubSearchTool` injected via a monkeypatched `_default_search_tool`, or via a `--stub` flag added later. Not building that today.

## Open questions

Captured separately in `notes/Implementation_Questions_cli.md`.
