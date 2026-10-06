"""Core logic for sleep duration parsing, clock targeting, and execution."""

import sys
import time
from datetime import datetime, timedelta


def parse_duration(duration_str: str) -> float:
    """
    Parse a duration string into total seconds.

    Supported formats:
      - SS (e.g. "10")
      - MM:SS (e.g. "01:30")
      - HH:MM:SS (e.g. "01:00:00")
      - [D]D[T][time_str] (e.g. "1D01:00:00", "1DT01:00:00", "2D10:00")
    """
    if not duration_str:
        raise ValueError("Duration cannot be empty.")

    days = 0
    time_str = duration_str

    if 'D' in duration_str:
        parts = duration_str.split('D', 1)
        if not parts[0].isdigit():
            raise ValueError(f"Invalid days format in duration: {duration_str}")
        days = int(parts[0])
        time_str = parts[1]
        if time_str.startswith('T'):
            time_str = time_str[1:]

    time_tokens = time_str.split(':')
    if len(time_tokens) > 3 or not all(token.isdigit() for token in time_tokens):
        raise ValueError(f"Invalid duration format: {duration_str}")

    time_parts = [int(p) for p in time_tokens]
    time_parts.reverse()

    seconds = time_parts[0] if len(time_parts) > 0 else 0
    minutes = time_parts[1] if len(time_parts) > 1 else 0
    hours = time_parts[2] if len(time_parts) > 2 else 0

    return float((days * 86400) + (hours * 3600) + (minutes * 60) + seconds)


def parse_until(until_str: str, now: datetime | None = None, auto_rollover: bool = True) -> tuple[float, datetime]:
    """
    Calculate sleep duration in seconds until a target time or timestamp.

    Supported formats:
      - HH:MM (e.g. "14:30")
      - HH:MM:SS (e.g. "14:30:00")
      - YYYY-MM-DDTHH:MM (e.g. "2026-10-06T15:00")
      - YYYY-MM-DDTHH:MM:SS (e.g. "2026-10-06T15:00:00")

    When given a daily clock time without a date that has already passed today:
      - If auto_rollover is True, rolls over to tomorrow.
      - If auto_rollover is False, raises ValueError.

    Explicit calendar datetimes in the past always raise ValueError.

    Returns:
      (sleep_seconds, target_datetime)
    """
    if not until_str:
        raise ValueError("Target time cannot be empty.")

    if now is None:
        now = datetime.now()

    target_str = until_str

    if 'T' not in target_str:
        parts = target_str.split(':')
        if len(parts) == 2:
            target_str += ":00"
        try:
            target_time = datetime.strptime(target_str, "%H:%M:%S")
        except ValueError as err:
            raise ValueError(f"Invalid time format for --until: {until_str}") from err

        target_datetime = now.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=target_time.second,
            microsecond=0
        )

        if target_datetime < now:
            if auto_rollover:
                target_datetime += timedelta(days=1)
            else:
                raise ValueError("The specified time is in the past.")
    else:
        date_part, time_part = target_str.split('T', 1)
        if len(time_part.split(':')) == 2:
            target_str += ":00"
        try:
            target_datetime = datetime.strptime(target_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError as err:
            raise ValueError(f"Invalid time format for --until: {until_str}") from err

        if target_datetime < now:
            raise ValueError("The specified time is in the past.")

    sleep_seconds = (target_datetime - now).total_seconds()
    return sleep_seconds, target_datetime


def calculate_modular_sleep(interval: float, now: datetime | None = None) -> float:
    """
    Calculate the remaining seconds to reach the next clock multiple.

    - interval <= 60: Snaps to multiples within the current minute (e.g. 10s -> :00, :10, :20, :30, :40, :50).
    - 60 < interval <= 3600: Snaps to multiples within the current hour (e.g. 300s [5m] -> :00, :05, :10, :15...).
    - interval > 3600: Snaps to multiples relative to midnight (e.g. 7200s [2h] -> 02:00, 04:00, 06:00...).
    """
    if interval <= 0:
        raise ValueError("Modular sleep interval must be positive.")

    if now is None:
        now = datetime.now()

    sub_second = now.microsecond / 1_000_000

    if interval <= 60:
        current_offset = now.second + sub_second
    elif interval <= 3600:
        current_offset = (now.minute * 60) + now.second + sub_second
    else:
        current_offset = (now.hour * 3600) + (now.minute * 60) + now.second + sub_second

    time_to_next_interval = interval - (current_offset % interval)

    if time_to_next_interval < 0.001:
        time_to_next_interval = interval

    return time_to_next_interval


def execute_sleep(sleep_seconds: float, verbose: bool = False) -> None:
    """
    Sleep for the specified number of seconds using time.monotonic() to eliminate drift.
    In verbose mode, updates an in-place terminal countdown.
    """
    if sleep_seconds <= 0:
        return

    start_monotonic = time.monotonic()
    target_end = start_monotonic + sleep_seconds

    while True:
        now_monotonic = time.monotonic()
        remaining = target_end - now_monotonic
        if remaining <= 0:
            break

        if verbose:
            remaining_td = timedelta(seconds=int(max(0, remaining)))
            sys.stdout.write(f"\r{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Sleeping for {remaining_td}")
            sys.stdout.flush()

        if remaining > 300:
            next_sleep = 300.0
        elif remaining > 60:
            next_sleep = remaining % 60 if remaining % 60 != 0 else 60.0
        elif remaining > 10:
            next_sleep = remaining % 10 if remaining % 10 != 0 else 10.0
        else:
            next_sleep = min(1.0, remaining)

        if next_sleep > remaining:
            next_sleep = remaining

        time.sleep(next_sleep)

    if verbose:
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
