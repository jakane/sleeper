"""Executable entry point when invoked via `python -m sleeper`."""

import sys
from sleeper.cli import main

if __name__ == "__main__":
    sys.exit(main())
