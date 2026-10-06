# sleeper

A smart, flexible command-line sleep utility written in Python. `sleeper` extends standard Unix `sleep` with human-friendly duration parsing, wall-clock time targeting, synchronized interval snapping ("modular sleep"), and dynamic countdown progress.

---

## Features

- **Flexible Duration Formats**: Specify durations in seconds (`10`), minutes and seconds (`01:30`), hours (`01:00:00`), or days (`1D04:00:00`).
- **Sleep Until a Specific Time (`--until`)**: Sleep until an exact time of day (`14:30`) or a specific calendar timestamp (`2026-12-25T08:00:00` or `2026-12-25T08:00`).
- **Modular Interval Snapping (Clock Alignment)**: Provide a bare positional duration (e.g., `sleeper 10`) to automatically synchronize with the next clock boundary (e.g., `:00`, `:10`, `:20`, `:30`, `:40`, `:50`). Perfect for keeping periodic loops aligned to real-time intervals.
- **Adaptive Visual Countdown (`-v`, `--verbose`)**: Displays a clean, in-place countdown timer in the terminal that dynamically updates as time elapses without clock drift.
- **Debug Explanation (`--debug`)**: Inspect how your input string was parsed and how the target sleep duration was calculated.
- **Clean Signal Handling**: Gracefully catches `Ctrl+C` (`SIGINT`), erasing verbose terminal lines and exiting cleanly with code 1 without dumping Python tracebacks.
- **Zero Runtime Dependencies**: Built entirely with the Python standard library.

---

## Installation

### Prerequisites
- Python 3.8+ installed.

### Option 1: Standard Python Package Installation (Recommended)
Install directly into your Python environment:
```bash
pip install .
```

Or for development (editable mode):
```bash
pip install -e .
```

Or via [pipx](https://pypa.github.io/pipx/):
```bash
pipx install .
```

### Option 2: Symlink to User Bin
Use the included install script to symlink `sleeper` into `~/.local/bin`:
```bash
./install.sh
```
Ensure `~/.local/bin` is in your shell's `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Usage

```text
sleeper [-h] [-v] [--debug] [--until UNTIL | --duration DURATION | duration_positional]
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
| `--until UNTIL` | Sleep until a target time (`HH:MM`, `HH:MM:SS`, or `YYYY-mm-ddTHH:MM[:SS]`). |
| `-v`, `--verbose` | Print a live countdown timer updating in-place. |
| `--debug` | Display detailed calculation info before sleeping. |
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
When writing shell loops, standard `sleep 10` causes timing drift because each loop iteration takes non-zero execution time.

Using bare positional seconds in `sleeper` automatically aligns execution to the next clock interval within the minute:
```bash
# Runs every 10 seconds, aligned to :00, :10, :20, :30, :40, :50 seconds on the clock
while true; do
    ./fetch-metrics.sh
    sleeper 10
done
```

To sleep for a fixed duration without modular snapping, use the `--duration` flag:
```bash
sleeper --duration 10
```

### 3. Target Time (`--until`)
Sleep until 4:30 PM today:
```bash
sleeper --until 16:30
```

Sleep until a specific future date and time:
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
sleeper --debug 10
```
*Output:*
```text
--- Debug Information ---
The positional argument '10' triggered modular sleep logic.
The requested interval is 10.00 seconds.
Current time in the minute is 34.215 seconds.
The initial sleep time of 10.00 seconds is being replaced.
The calculated sleep time is 5.785 seconds to reach the next interval.
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
