# Agent Testing Workshop -- Research Summarizer Agent

Attendees for this workshop should complete the prerequisites and the setup sections before the workshop. Please raise an issue on the repository if you have trouble.

[Workshop presentation deck](docs/The-AI-Agent-Testing-Pyramid-Workshop-London-2026.pdf)

## Prerequisites

> Attendees need the fllowing software installed.

- Claude Code installed and working (we will be using it extensively)
- Python 3.11, 3.12, or 3.13.
- Anthropic API key with access to `claude-haiku-4-5-20251001` and `claude-sonnet-4-6` (the eval judge). Instructions are [here](https://support.claude.com/en/articles/8114521-how-can-i-access-the-claude-api).
- Tavily API key (free tier is enough for the workshop). Signup is [here](https://www.tavily.com/?utm_term=tavily%20key&utm_campaign=Tavily+Brand+-+General+-+noram&utm_source=adwords&utm_medium=ppc&matchtype=e&device=c&utm_content=799226621414_&utm_position=&gad_source=1&gad_campaignid=23618630592&gbraid=0AAAABB_ZBWrGxPB26jWzy_RrBzm53gyt3&gclid=CjwKCAjwtvvPBhBuEiwAPMijrxnL17B8nRYAEjeS5TOG8awtuVjlq-0GjQdSKJ9_IyM4OpcjmAG2bhoCyVUQAvD_BwE)

> Note:  In developing and writing the test solutions in preparation for this workshop, I spent less than $1 USD for my Anthropic Key.My Tavily usage was well within the free tier threshold. 

Costs for this workshop are expected to be low. 

## Setup

> Fork the repository

This isn't strictly needed, but it allows you to keep your work.

> Clone the repository locally

> Install the Python dependencies and verify setup.

- At a command prompt, change your current directory to the root folder for the repository clone. 
- Execute the bash commands below. A slight adjustment if you're using Windows.

```bash
python3 -m venv .venv
source .venv/bin/activate          # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste in your two API keys.
python3 verify_setup.py
```

`verify_setup.py` exits 0 when everything is wired up; exits 1 otherwise.

# Workshop Exercises

This workshop teaches how to test a non-deterministic AI agent by climbing the **AI Agent Testing Pyramid** — from fast, mocked unit tests at the base to human review at the top. You will implement each tier against the same small research-summarizer agent, using Claude Code as your pair programmer.

The pyramid model is defined in [requirements/Testing-Pyramid.md](requirements/Testing-Pyramid.md). For the full motivation, trade-offs, and how the tiers fit together, see [The AI Agent Testing Pyramid: A Practical Framework for Non-Deterministic Systems](https://medium.com/@derekcashmore/the-ai-agent-testing-pyramid-a-practical-framework-for-non-deterministic-systems-276c22feaec8) on Medium.

Work through the four exercises **in order**. Each file contains suggested Claude Code prompts; earlier levels should stay green before you move on.

| Level | Tier | Exercise |
|-------|------|----------|
| 1 | Base — deterministic unit tests | [exercises/level1_prompts.md](exercises/level1_prompts.md) |
| 2 | Lower-middle — constrained model tests | [exercises/level2_prompts.md](exercises/level2_prompts.md) |
| 3 | Upper-middle — LLM-as-judge evals | [exercises/level3_prompts.md](exercises/level3_prompts.md) |
| 4 | Top — human evaluation | [exercises/level4_prompts.md](exercises/level4_prompts.md) |

**Level 1** stubs the search tool and tests orchestration (validation, empty results, happy path) without API calls. 

**Level 2** calls the real model with controlled settings to check structured output and prompt behavior. 

**Level 3** adds an automated judge to grade semantic quality. 

**Level 4** covers preference testing, expert review, and red-teaming — the expensive signal you use sparingly in production.

# How the agent works

`from agent import summarize` exposes the single public entry point. Internally it walks five short steps: validate input, call the search tool, format a user message, call Claude with a forced `tool_use` for structured output, parse the result. The full source under `agent/` is well under 250 lines combined; reading it end-to-end takes less than ten minutes.

For the full design rationale and field semantics, see `requirements/Research_Summarizer_Agent_Spec.md`. The build plan that produced this code is in `plans/ImplementationPlan.md`.

## Running the CLI

A small CLI ships with the agent so attendees can drive it without writing Python. It takes a single positional `topic` argument:

```bash
python3 -m agent "photosynthesis"            # plain-text output to stdout
python3 -m agent --json "quantum computing"  # SummaryResult as indented JSON
```

The CLI reads `ANTHROPIC_API_KEY` and (optionally) `TAVILY_API_KEY` from the environment, the same as the library. Without `TAVILY_API_KEY` the agent raises `NoResultsError`, which the CLI prints to stderr and exits with code 1. Errors are written to stderr in the form `error: <ExceptionClass>: <message>`; on success the exit code is 0.

```bash
python3 -m agent --help
```

## Running tests

```bash
pytest3 tests/test_level1.py     # fast, no API calls
pytest3 tests/test_level2.py     # uses real Anthropic + Tavily; skips if keys missing
```

The starter files in `tests/` are commented stubs — fill them in during the workshop. Reference solutions live in `solution/tests/`.

## Running the eval

```bash
python3 evals/judge_eval.py
```

The script calls the agent, then asks `claude-sonnet-4-6` to grade the output on four pass/fail dimensions. Stdout shows a labelled report; the structured trace is written to `sample_outputs/judge_eval_run.json` (committed in the repo as a known-good example run).

## Design choices

- **Pydantic v2** so `model_json_schema()` produces the structured-output tool schema for Anthropic without manual JSON wrestling.
- **Anthropic native `tool_use`** (forced via `tool_choice`) for structured output — no `instructor` dependency, one fewer abstraction layer to read.
- **Pinned model name** (`claude-haiku-4-5-20251001`), never an alias. Aliased names can silently change behavior between build day and workshop day; the pin makes the workshop reproducible. Pinning is itself a teaching point.

Pin date: **2026-05-03**. If the workshop is more than ~30 days from this date, refresh the pins (see playbook below) and re-run the eval before the session.

## Pin-refresh playbook

```bash
pip install -U anthropic pydantic tavily-python pytest python-dotenv
pip freeze > requirements-lock.txt
# Manually update top-level pins in requirements.txt to the new versions.
# If prompts or models changed, also re-run the eval and commit the new trace:
python3 evals/judge_eval.py
```

## Sample outputs

`sample_outputs/photosynthesis.json` and `sample_outputs/quantum_computing.json` are hand-curated examples of the `SummaryResult` shape with real, stable URLs (Wikipedia, NIH, quantum.gov). Verify the URLs are still live before each session:

```bash
python3 scripts/check_sample_urls.py
```

Exit code 0 means every citation URL returned HTTP 200.

## Troubleshooting

| Symptom (from `verify_setup.py`) | Fix |
|---|---|
| `FAIL: Python ...` | Install Python 3.11–3.13 and re-create the venv. |
| `FAIL: package '...' not importable` | `pip install -r requirements.txt` from inside the venv. |
| `FAIL: ANTHROPIC_API_KEY not set` | Paste your key into `.env` (or `export` it). |
| `FAIL: Anthropic API call failed` | Confirm the key is valid and that your org has access to `claude-haiku-4-5-20251001`. |
| `WARN: TAVILY_API_KEY not set` | Optional — the agent will raise `NoResultsError` on every call without it. Get a key at https://app.tavily.com if you want Level 2 to run end-to-end. |

## Note for attendees

The `solution/` directory contains the instructor reference: completed Level 1 and Level 2 tests plus a defects writeup. You can ignore it during the workshop.
