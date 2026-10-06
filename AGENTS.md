# AGENTS.md

This document provides context, architectural guidelines, development practices, and testing instructions for AI coding agents and automated systems working on the `sleeper` codebase.

---

## 1. Project Overview & Philosophy

`sleeper` is a lightweight, zero-runtime-dependency command-line utility structured as a standard Python package (`src`-layout). It is designed to be:
- **Zero third-party dependencies**: Implemented purely using the Python 3 standard library.
- **Fast and lightweight**: Minimal import overhead for instant CLI invocation.
- **Standard Python Packaging**: Configured via `pyproject.toml` (PEP 517/621) with console script entry points.
- **Clock-synchronized ("Modular sleep")**: Capable of synchronizing periodic loops to multi-scale wall-clock intervals (seconds within minute, minutes within hour, hours within day).
- **Intelligent Target Sleep**: Automatically rolls past daily target times to the following day.
- **Interactive & Observant**: Features an in-place visual countdown timer (`-v`) and calculation introspection (`--debug`).

---

## 2. Repository Layout

```text
sleeper/
├── pyproject.toml         # PEP 517/621 build config & script entry point (sleeper = sleeper.cli:main)
├── .gitignore             # Git ignore patterns for Python, builds, tests
├── README.md              # User manual, installation, and usage examples
├── AGENTS.md              # Developer and agent guidance (this file)
├── install.sh             # Shell script symlinking ./sleeper to ~/.local/bin/sleeper
├── sleeper                # Root executable launcher (convenient for local dev & symlinks)
├── src/
│   └── sleeper/
│       ├── __init__.py    # Package definition & __version__
│       ├── __main__.py    # Module execution entry point (python3 -m sleeper)
│       ├── cli.py         # Argument parsing, debug formatting, signal handling
│       └── core.py        # Core logic: duration parsing, timestamp logic, modular math, sleep loop
└── tests/
    ├── __init__.py
    ├── test_core.py       # Unit tests for duration/timestamp parsing, modular arithmetic, sleep loop
    └── test_cli.py        # CLI invocation, argument validation, and flag behavior
```

---

## 3. Architecture & Key Modules

### `src/sleeper/core.py`
Contains pure computation and execution functions:
- `parse_duration(duration_str: str) -> float`: Parses `SS`, `MM:SS`, `HH:MM:SS`, and `[D]D[T][time_str]` formats into seconds.
- `parse_until(until_str: str, now: datetime | None = None, auto_rollover: bool = True) -> tuple[float, datetime]`: Parses clock time (`HH:MM[:SS]`) and ISO timestamps (`YYYY-MM-DDTHH:MM[:SS]`). Automatically rolls past clock times to tomorrow when `auto_rollover` is enabled.
- `calculate_modular_sleep(interval: float, now: datetime | None = None) -> float`: Multi-scale clock snapping:
  - $\le 60\text{s}$: Snaps within the current minute (e.g. `10` -> `:00, :10, :20...`; `60` -> top of the minute).
  - $60\text{s} < \text{interval} \le 3600\text{s}$: Snaps within the current hour (e.g. `300` -> 5-minute boundaries `:00, :05, :10...`).
  - $> 3600\text{s}$: Snaps within the current day relative to midnight.
- `execute_sleep(sleep_seconds: float, verbose: bool = False) -> None`: Runs an adaptive sleep loop using `time.monotonic()` to eliminate timing drift while providing in-place countdown updates (`\r`).

### `src/sleeper/cli.py`
Handles command-line interactions:
- `build_parser() -> argparse.ArgumentParser`: Configures flags (`-v`, `--debug`, `-V`/`--version`) and mutually exclusive groups (`--until`, `--duration`, `duration_positional`).
- `main(argv=None) -> int`: Parses arguments, dispatches to `core` functions, formats `--debug` output, intercepts `KeyboardInterrupt` for clean terminal teardown, and returns POSIX exit codes (`0` or `1`).

### `src/sleeper/__main__.py`
Allows direct module execution via `python3 -m sleeper`.

### `sleeper` (Root Launcher)
A thin executable script that adds `src/` to `sys.path` and calls `sleeper.cli.main()`. This allows immediate local execution (`./sleeper`) and preserves backward compatibility with `install.sh`.

---

## 4. Development & Contribution Rules

1. **Zero External Runtime Dependencies**:
   - All runtime code must strictly rely on Python standard library modules (`sys`, `time`, `datetime`, `argparse`, `pathlib`).
2. **Preserve CLI Interface Contracts**:
   - Backward compatibility for existing CLI syntax is mandatory (`sleeper 10`, `sleeper 01:30`, `sleeper --until 14:00`, `sleeper -v`).
   - Bare positional arguments must continue triggering modular interval sleep.
3. **Clean Exit and Terminal Integrity**:
   - Never allow uncaught `KeyboardInterrupt` tracebacks to be dumped to `stderr`.
   - Always clear any carriage return (`\r`) lines before printing messages or exiting.
4. **Drift-Free Timing**:
   - Always reference `time.monotonic()` for interval/duration tracking in loops rather than accumulating nominal sleep increments.
5. **Always Use Python Virtual Environments**:
   - Always create and use a dedicated virtual environment (`.venv/`) for local development, package builds, and testing. Never install packages or run tests directly against global system/Homebrew Python environments.

---

## 5. Testing & Verification

Always run tests within the project's virtual environment:
```bash
# Create and activate virtual environment (if not already present)
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e .

# Run test suite
python -m unittest discover -v -s tests
```

### Manual CLI Checks
```bash
# Verify launcher directly
./sleeper --help
./sleeper --debug 60    # Snaps to top of minute
./sleeper --debug 300   # Snaps to 5-minute mark
./sleeper --debug --until 08:00  # Verifies tomorrow rollover if run after 8am

# Verify module execution
PYTHONPATH=src python3 -m sleeper --help

# Verify unit tests pass with zero errors
PYTHONPATH=src python3 -m unittest discover -s tests
```
