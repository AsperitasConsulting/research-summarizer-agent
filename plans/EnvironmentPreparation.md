# Environment Preparation: Research Summarizer Agent

**Date assessed:** 2026-05-03
**Python version on this machine:** 3.12.3
**pip version:** 25.2

---

## Summary

The local environment is mostly ready. One package (`tavily-python`) is missing and must be installed before the implementation phases that call the Tavily Search API.

---

## Python Version

| Requirement | Current | Status |
|---|---|---|
| `>=3.11, <3.14` | 3.12.3 | PASS |

No action required.

---

## Required Packages

Assessed against the `requirements.txt` pins specified in the implementation plan (Phase 1.2).

| Package | Required Version | Installed Version | Status | Action |
|---|---|---|---|---|
| `anthropic` | `>=X.Y.Z,<NEXT_MAJOR` (latest stable) | 0.64.0 | PASS | None |
| `pydantic` | `>=2.7,<3` | 2.11.7 | PASS | None |
| `tavily-python` | `>=0.5,<1` | NOT INSTALLED | **FAIL** | Install (see below) |
| `pytest` | `>=8,<9` | 8.4.1 | PASS | None |
| `python-dotenv` | `>=1,<2` | 1.1.1 | PASS | None |

---

## Required Installs / Upgrades

### 1. Install `tavily-python`

```bash
pip install "tavily-python>=0.5,<1"
```

This is the only missing dependency. After installing, confirm the version with:

```bash
pip show tavily-python
```

### 2. Create and populate `.env` file

The agent reads configuration from environment variables. Copy the template and fill in your keys:

```bash
cp .env.example .env
```

Then edit `.env`:

```
# Required
ANTHROPIC_API_KEY=sk-ant-...your-key-here...

# Optional — if absent, StubSearchTool is used (agent raises NoResultsError on any call)
TAVILY_API_KEY=tvly-...your-key-here...

# Optional instructor overrides (do not set unless you know what you're doing)
# SUMMARIZER_MODEL=claude-haiku-4-5-20251001
# SUMMARIZER_TEMPERATURE=1.0
```

### 3. Lock dependencies after install

Per Phase 1.2 of the implementation plan, after installing all packages:

```bash
pip freeze > requirements-lock.txt
```

Then update `requirements.txt` to replace the placeholder version bounds with the exact resolved versions (e.g., `anthropic==0.64.0`), and commit both files.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | — | Anthropic API key. Required for all real LLM calls and for Level 2 tests. `verify_setup.py` will fail without it. |
| `TAVILY_API_KEY` | No | — | Tavily Search API key. If absent, `StubSearchTool` is used and `summarize()` will raise `NoResultsError` on every call. `verify_setup.py` emits a WARN (not FAIL) if absent. |
| `SUMMARIZER_MODEL` | No | `claude-haiku-4-5-20251001` | Override the pinned model. For instructor use only; do not set during normal workshop operation. |
| `SUMMARIZER_TEMPERATURE` | No | `1.0` | Override temperature. Level 2 tests set this to `0` via `monkeypatch`; you do not need to set it in `.env` for tests. |

---

## Obtaining API Keys

### Anthropic API Key

1. Sign in at [console.anthropic.com](https://console.anthropic.com).
2. Navigate to **API Keys** and create a new key.
3. The key begins with `sk-ant-`.
4. Ensure the key has access to `claude-haiku-4-5-20251001` (the pinned model) and `claude-sonnet-4-6` (used by the eval judge).

### Tavily API Key

1. Sign up at [app.tavily.com](https://app.tavily.com).
2. The free tier provides enough quota for workshop development and testing.
3. The key begins with `tvly-`.
4. Per the implementation plan (Phase 1, Q16 v2), `verify_setup.py` confirms the key is present but does **not** make a live Tavily call during setup verification.

---

## Verification

After completing the steps above, run the pre-workshop self-check:

```bash
python verify_setup.py
```

Expected output (all keys present):

```
PASS: Python 3.12.3 (>= 3.11, < 3.14)
PASS: anthropic 0.64.0
PASS: pydantic 2.11.7
PASS: tavily-python X.Y.Z
PASS: pytest 8.4.1
PASS: python-dotenv 1.1.1
PASS: ANTHROPIC_API_KEY set (sk-ant-...XYZ)
PASS: Anthropic API call succeeded in Xms
PASS: TAVILY_API_KEY set (tvly-...XYZ)
```

Exit code 0 indicates full readiness.

---

## Pre-Workshop URL Check

After sample outputs are generated (Phase 13), run the URL link checker before each workshop session to verify citations are still live:

```bash
python scripts/check_sample_urls.py
```

Exit code 0 means all citation URLs resolve to HTTP 200.
