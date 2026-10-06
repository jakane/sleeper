"""Unit tests for sleeper core module."""

import unittest
from datetime import datetime
from io import StringIO
import sys

from sleeper.core import (
    calculate_modular_sleep,
    execute_sleep,
    parse_duration,
    parse_until,
)


class TestParseDuration(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(parse_duration("0"), 0.0)
        self.assertEqual(parse_duration("10"), 10.0)
        self.assertEqual(parse_duration("45"), 45.0)

    def test_minutes_seconds(self):
        self.assertEqual(parse_duration("01:30"), 90.0)
        self.assertEqual(parse_duration("10:00"), 600.0)

    def test_hours_minutes_seconds(self):
        self.assertEqual(parse_duration("01:00:00"), 3600.0)
        self.assertEqual(parse_duration("02:15:30"), 8130.0)

    def test_days(self):
        self.assertEqual(parse_duration("1D00:00:00"), 86400.0)
        self.assertEqual(parse_duration("1D01:00:00"), 90000.0)
        self.assertEqual(parse_duration("1DT01:00:00"), 90000.0)
        self.assertEqual(parse_duration("2D10:00"), 173400.0)

    def test_invalid_formats(self):
        with self.assertRaises(ValueError):
            parse_duration("")
        with self.assertRaises(ValueError):
            parse_duration("abc")
        with self.assertRaises(ValueError):
            parse_duration("-5")
        with self.assertRaises(ValueError):
            parse_duration("1:2:3:4")
        with self.assertRaises(ValueError):
            parse_duration("AD01:00:00")


class TestParseUntil(unittest.TestCase):
    def test_clock_time(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        seconds, target_dt = parse_until("14:30", now=now)
        self.assertEqual(seconds, 1800.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 14, 30, 0))

        seconds, target_dt = parse_until("14:30:15", now=now)
        self.assertEqual(seconds, 1815.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 14, 30, 15))

    def test_iso_timestamp(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        # Without seconds (previously failed in original sleeper)
        seconds, target_dt = parse_until("2026-10-06T15:00", now=now)
        self.assertEqual(seconds, 3600.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 15, 0, 0))

        # With seconds
        seconds, target_dt = parse_until("2026-10-06T15:00:45", now=now)
        self.assertEqual(seconds, 3645.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 15, 0, 45))

    def test_past_time_raises(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        with self.assertRaises(ValueError):
            parse_until("13:59:59", now=now)

    def test_invalid_time_format(self):
        with self.assertRaises(ValueError):
            parse_until("")
        with self.assertRaises(ValueError):
            parse_until("not-a-time")


class TestModularSleep(unittest.TestCase):
    def test_modulo_calculation(self):
        # Current second is 14.0, interval is 10 -> next interval at 20.0 (6.0s remaining)
        now = datetime(2026, 10, 6, 14, 0, 14, 0)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 6.0)

        # Current second is 14.25
        now = datetime(2026, 10, 6, 14, 0, 14, 250000)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 5.75)

    def test_boundary_snaps_to_full_interval(self):
        # Exactly on the boundary (second 20.0) -> next is 30.0 (10.0s remaining)
        now = datetime(2026, 10, 6, 14, 0, 20, 0)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 10.0)


class TestExecuteSleep(unittest.TestCase):
    def test_zero_sleep(self):
        execute_sleep(0.0)

    def test_short_sleep(self):
        execute_sleep(0.01, verbose=False)

    def test_short_sleep_verbose(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            execute_sleep(0.01, verbose=True)
            output = sys.stdout.getvalue()
            self.assertIn("Sleeping for", output)
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
