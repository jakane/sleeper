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
        seconds, target_dt = parse_until("2026-10-06T15:00", now=now)
        self.assertEqual(seconds, 3600.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 15, 0, 0))

        seconds, target_dt = parse_until("2026-10-06T15:00:45", now=now)
        self.assertEqual(seconds, 3645.0)
        self.assertEqual(target_dt, datetime(2026, 10, 6, 15, 0, 45))

    def test_past_clock_time_rolls_over_to_tomorrow(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        # 13:00 has already passed today; rolls over to 13:00 tomorrow (23 hours = 82800s)
        seconds, target_dt = parse_until("13:00", now=now, auto_rollover=True)
        self.assertEqual(seconds, 82800.0)
        self.assertEqual(target_dt, datetime(2026, 10, 7, 13, 0, 0))

    def test_past_clock_time_without_rollover_raises(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        with self.assertRaises(ValueError):
            parse_until("13:00", now=now, auto_rollover=False)

    def test_past_calendar_datetime_raises(self):
        now = datetime(2026, 10, 6, 14, 0, 0)
        with self.assertRaises(ValueError):
            parse_until("2026-10-05T13:00", now=now, auto_rollover=True)

    def test_invalid_time_format(self):
        with self.assertRaises(ValueError):
            parse_until("")
        with self.assertRaises(ValueError):
            parse_until("not-a-time")


class TestModularSleep(unittest.TestCase):
    def test_sub_minute_modulo(self):
        now = datetime(2026, 10, 6, 14, 0, 14, 0)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 6.0)

        now = datetime(2026, 10, 6, 14, 0, 14, 250000)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 5.75)

    def test_boundary_snaps_to_full_interval(self):
        now = datetime(2026, 10, 6, 14, 0, 20, 0)
        remaining = calculate_modular_sleep(10.0, now=now)
        self.assertAlmostEqual(remaining, 10.0)

    def test_top_of_minute_modulo(self):
        now = datetime(2026, 10, 6, 14, 5, 25, 0)
        remaining = calculate_modular_sleep(60.0, now=now)
        self.assertAlmostEqual(remaining, 35.0)

    def test_multi_minute_snapping_5_minutes(self):
        # 14:02:15 -> next 5m mark is 14:05:00 (165s remaining)
        now = datetime(2026, 10, 6, 14, 2, 15, 0)
        remaining = calculate_modular_sleep(300.0, now=now)
        self.assertAlmostEqual(remaining, 165.0)

    def test_quarter_hour_snapping_15_minutes(self):
        # 14:08:00 -> next 15m mark is 14:15:00 (420s remaining)
        now = datetime(2026, 10, 6, 14, 8, 0, 0)
        remaining = calculate_modular_sleep(900.0, now=now)
        self.assertAlmostEqual(remaining, 420.0)

    def test_multi_hour_snapping(self):
        # 09:15:00 -> next 2h mark is 10:00:00 (45m = 2700s remaining)
        now = datetime(2026, 10, 6, 9, 15, 0, 0)
        remaining = calculate_modular_sleep(7200.0, now=now)
        self.assertAlmostEqual(remaining, 2700.0)


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
