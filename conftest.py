"""Project-root conftest.

Pytest needs the project root on ``sys.path`` so that ``from agent import ...``
resolves cleanly regardless of which test directory is collected. Placing this
file at the repo root achieves that without a ``pyproject.toml`` build config.
"""
