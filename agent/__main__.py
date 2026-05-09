"""Allow ``python -m agent <topic>`` to invoke the CLI."""

from agent.cli import main

raise SystemExit(main())
