"""Pre-workshop URL link checker.

Iterates every citation URL in ``sample_outputs/*.json`` (excluding
``judge_eval_run.json``) and confirms each returns HTTP 200.

Run::

    python scripts/check_sample_urls.py

Exit code 0 = every URL returned 200. Exit code 1 = any URL returned non-200,
timed out, or failed DNS.

Run before each workshop session — if the sample URLs have rotted, the
samples are misleading.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


_TIMEOUT_SECONDS = 5
_USER_AGENT = "research-summarizer-link-check/1.0"


def _check(url: str) -> tuple[int | None, int]:
    """GET ``url`` and return ``(status_code, elapsed_ms)``.

    ``status_code`` is ``None`` for timeouts, DNS failures, or other transport
    errors. The response body is read and discarded to release the connection.
    """
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            response.read()
            elapsed_ms = int((time.monotonic() - started) * 1000)
            return response.status, elapsed_ms
    except urllib.error.HTTPError as http_err:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return http_err.code, elapsed_ms
    except (urllib.error.URLError, TimeoutError, OSError):
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return None, elapsed_ms


def main() -> int:
    sample_dir = Path(__file__).resolve().parent.parent / "sample_outputs"
    files = sorted(p for p in sample_dir.glob("*.json") if p.name != "judge_eval_run.json")
    if not files:
        print("No sample files to check.", file=sys.stderr)
        return 1

    failures = 0
    for path in files:
        data = json.loads(path.read_text())
        for citation in data.get("citations", []):
            url = citation.get("url", "")
            status, elapsed_ms = _check(url)
            status_str = str(status) if status is not None else "ERR"
            print(f"{path.name} | {url} | {status_str} | {elapsed_ms}ms")
            if status != 200:
                failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
