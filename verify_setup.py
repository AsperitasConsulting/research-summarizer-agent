"""Pre-workshop environment self-check.

Exit codes:
    0 — all required checks passed (WARN allowed)
    1 — at least one required check failed

Each check prints a single ``PASS:`` / ``FAIL:`` / ``WARN:`` line followed
by short diagnostic detail. Output is plain text suitable for screen-share.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import os
import sys
import time
from typing import Iterable

from dotenv import load_dotenv


load_dotenv()

REQUIRED_PACKAGES: tuple[str, ...] = (
    "anthropic",
    "pydantic",
    "tavily",
    "pytest",
    "dotenv",
)

# importlib.metadata uses distribution names rather than import names.
DISTRIBUTION_NAMES: dict[str, str] = {
    "tavily": "tavily-python",
    "dotenv": "python-dotenv",
}


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return f"{key[:7]}...{key[-3:]}"


def _check_python_version() -> bool:
    major, minor = sys.version_info[:2]
    in_range = (major, minor) >= (3, 11) and (major, minor) < (3, 14)
    label = "PASS" if in_range else "FAIL"
    print(f"{label}: Python {sys.version.split()[0]} (require >= 3.11, < 3.14)")
    if not in_range:
        print("       Hint: install a Python 3.11, 3.12, or 3.13 interpreter and re-create the virtualenv.")
    return in_range


def _check_packages(packages: Iterable[str]) -> bool:
    all_ok = True
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError as exc:
            print(f"FAIL: package '{pkg}' is not importable ({exc}).")
            print(f"       Hint: pip install -r requirements.txt")
            all_ok = False
            continue
        dist = DISTRIBUTION_NAMES.get(pkg, pkg)
        try:
            version = importlib.metadata.version(dist)
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        print(f"PASS: {dist} {version}")
    return all_ok


def _check_anthropic_key() -> bool:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("FAIL: ANTHROPIC_API_KEY not set.")
        print("       Hint: add it to your .env file or export it: export ANTHROPIC_API_KEY=sk-ant-...")
        return False
    print(f"PASS: ANTHROPIC_API_KEY set ({_mask_key(key)})")
    return True


def _check_anthropic_call() -> bool:
    try:
        import anthropic
    except ImportError:
        print("FAIL: cannot test Anthropic API call — anthropic package not installed.")
        return False
    model = "claude-haiku-4-5-20251001"
    started = time.monotonic()
    try:
        client = anthropic.Anthropic()
        client.messages.create(
            model=model,
            max_tokens=1,
            messages=[{"role": "user", "content": "ok"}],
        )
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        print(f"FAIL: Anthropic API call failed after {elapsed_ms}ms: {type(exc).__name__}: {exc}")
        print("       Hint: check that ANTHROPIC_API_KEY is valid and has access to claude-haiku-4-5-20251001.")
        return False
    elapsed_ms = int((time.monotonic() - started) * 1000)
    print(f"PASS: Anthropic API call ({model}) succeeded in {elapsed_ms}ms")
    return True


def _check_tavily_key() -> bool:
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        print("WARN: TAVILY_API_KEY not set.")
        print("       Without it, the agent uses StubSearchTool and raises NoResultsError on every call.")
        print("       Get a free-tier key at https://app.tavily.com if you want Level 2 to run end-to-end.")
        return True  # warn does not fail
    print(f"PASS: TAVILY_API_KEY set ({_mask_key(key)})")
    return True


def main() -> int:
    checks = [
        _check_python_version,
        lambda: _check_packages(REQUIRED_PACKAGES),
        _check_anthropic_key,
        _check_anthropic_call,
        _check_tavily_key,
    ]
    results = [check() for check in checks]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
