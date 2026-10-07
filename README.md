# sleeper

A smart, flexible command-line sleep utility written in Python. `sleeper` extends standard Unix `sleep` with human-friendly duration parsing, wall-clock time targeting with automatic rollover, synchronized interval snapping ("modular sleep"), and dynamic countdown progress.

---

## Features

- **Flexible Duration Formats**: Specify durations in seconds (`10`), minutes and seconds (`01:30`), hours (`01:00:00`), or days (`1D04:00:00`).
- **Sleep Until a Specific Time (`--until`)**: Sleep until an exact time of day (`14:30`) or a specific calendar timestamp (`2026-12-25T08:00:00`).
- **Smart Next-Day Rollover**: If a daily clock time passed to `--until` has already occurred today (e.g., `--until 08:00` run in the afternoon), `sleeper` automatically rolls over to target that time tomorrow.
- **Multi-Scale Modular Interval Snapping**: Provide a bare positional duration to synchronize with clock boundaries:
  - $\le 60\text{s}$ (e.g., `sleeper 10`): Snaps to `:00, :10, :20, :30, :40, :50` within the minute.
  - `sleeper 60`: Snaps directly to the **top of the next minute** (`:00`).
  - $> 60\text{s}$ (e.g., `sleeper 300` or `sleeper 900`): Snaps to 5-minute or quarter-hour clock boundaries on the wall clock.
  - Multi-hour (e.g., `sleeper 7200`): Snaps to 2-hour boundaries relative to midnight.
- **Adaptive Visual Countdown (`-v`, `--verbose`)**: Displays a clean, in-place countdown timer in the terminal that dynamically updates as time elapses without clock drift (powered by `time.monotonic()`).
- **Debug Explanation (`--debug`)**: Inspect how your input string was parsed and how the target sleep duration was calculated.
- **Clean Signal Handling**: Gracefully catches `Ctrl+C` (`SIGINT`), erasing verbose terminal lines and exiting cleanly with code 1 without dumping Python tracebacks.
- **Zero Runtime Dependencies**: Built entirely with the Python standard library.

---

## Installation

### Prerequisites
- Python 3.8+ installed.

### Option 1: Standard Python Package Installation (Recommended)
Set up and activate a virtual environment, then install:
```bash
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install .

# Or for development (editable mode)
pip install -e .
```

Or install as an isolated CLI tool via [pipx](https://pypa.github.io/pipx/):
```bash
pipx install .
```

### Option 2: Standalone User Executable
Build and install a standalone, self-contained executable to `~/.local/bin` (using Python's built-in `zipapp`, requiring no venv or cloned repo at runtime):
```bash
make install-user
```
Ensure `~/.local/bin` is in your shell's `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Usage

```text
sleeper [-h] [-v] [-V] [--debug] [--until UNTIL | --duration DURATION | duration_positional]
```

Or invoke as a Python module:
```bash
python3 -m sleeper [options]
```

### Options

| Flag / Argument | Description |
| :--- | :--- |
| `duration_positional` | Sleep for a duration (`SS`, `MM:SS`, or `HH:MM:SS`). A single integer activates **modular sleep**. |
| `--duration DURATION` | Sleep for a specified duration (`[[[DD]D]HH:]MM:]SS`). Does not snap to clock intervals. |
| `--until UNTIL` | Sleep until a target time (`HH:MM`, `HH:MM:SS`, or `YYYY-mm-ddTHH:MM[:SS]`). Automatically rolls over past daily times to tomorrow. |
| `-v`, `--verbose` | Print a live countdown timer updating in-place. |
| `--debug` | Display detailed calculation info before sleeping. |
| `-V`, `--version` | Show program version and exit. |
| `-h`, `--help` | Show command usage and argument definitions. |

---

## Examples

### 1. Basic Sleep
Sleep for 15 seconds:
```bash
sleeper 15
```

Sleep for 1 minute and 30 seconds:
```bash
sleeper 01:30
```

Sleep for 2 hours, 15 minutes, and 30 seconds:
```bash
sleeper 02:15:30
```

### 2. Modular Sleep (Loop Synchronization)
Standard `sleep` causes cumulative timing drift in loops because script execution takes non-zero time. 

Passing a bare positional integer activates modular snapping:
```bash
# Sleep to the top of the next minute (:00)
sleeper 60

# Runs every 10 seconds, aligned to :00, :10, :20, :30, :40, :50
while true; do
    ./fetch-metrics.sh
    sleeper 10
done

# Aligns execution to every 5-minute mark on the clock (:00, :05, :10, :15...)
while true; do
    ./sync-data.sh
    sleeper 300
done
```

To sleep for a fixed duration without modular snapping, use `--duration` or a formatted string:
```bash
sleeper --duration 60
sleeper 01:00
```

### 3. Target Time (`--until`) & Automatic Rollover
Sleep until 4:30 PM today:
```bash
sleeper --until 16:30
```

If it is currently 3:00 PM and you specify `--until 08:00`, `sleeper` automatically rolls over to 8:00 AM tomorrow:
```bash
sleeper --until 08:00
```

Sleep until a specific calendar date and time:
```bash
sleeper --until 2026-12-31T23:59:00
```

### 4. Progress Countdown & Debugging
Display an active countdown timer:
```bash
sleeper -v 05:00
```

Inspect calculation logic with `--debug`:
```bash
sleeper --debug 60
```
*Output:*
```text
--- Debug Information ---
The positional argument '60' triggered modular sleep logic.
The requested interval is 60.00 seconds.
Current time in the minute is 34.875 seconds.
The initial sleep time of 60.00 seconds is being replaced.
The calculated sleep time is 25.125 seconds to reach the next interval.
-------------------------
```

---

## Running Tests

Run the test suite using Python's standard `unittest`:
```bash
python3 -m unittest discover -s tests
```
Or with `pytest`:
```bash
pytest
```

---

## License

MIT License. See repository history for attribution.
