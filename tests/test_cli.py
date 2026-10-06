"""Unit tests for sleeper CLI module."""

import unittest
from unittest.mock import patch
from io import StringIO
import sys
from datetime import datetime

from sleeper.cli import build_parser, main


class TestCLIParser(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_empty_arguments(self):
        args = self.parser.parse_args([])
        self.assertIsNone(args.until)
        self.assertIsNone(args.duration)
        self.assertIsNone(args.duration_positional)
        self.assertFalse(args.verbose)
        self.assertFalse(args.debug)

    def test_duration_positional(self):
        args = self.parser.parse_args(["15"])
        self.assertEqual(args.duration_positional, "15")

    def test_duration_flag(self):
        args = self.parser.parse_args(["--duration", "01:30"])
        self.assertEqual(args.duration, "01:30")

    def test_until_flag(self):
        args = self.parser.parse_args(["--until", "16:00"])
        self.assertEqual(args.until, "16:00")

    def test_mutually_exclusive_flags(self):
        with patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                self.parser.parse_args(["--until", "16:00", "--duration", "10"])

    def test_version_flags(self):
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with self.assertRaises(SystemExit) as cm:
                self.parser.parse_args(["--version"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("sleeper 0.0.1", fake_stdout.getvalue())

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with self.assertRaises(SystemExit) as cm:
                self.parser.parse_args(["-V"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("sleeper 0.0.1", fake_stdout.getvalue())


class TestCLIMain(unittest.TestCase):
    def test_no_args_prints_help(self):
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main([])
            self.assertEqual(exit_code, 0)
            self.assertIn("usage: sleeper", fake_stdout.getvalue())

    def test_invalid_duration_returns_1(self):
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            exit_code = main(["not-a-number"])
            self.assertEqual(exit_code, 1)
            self.assertIn("Error:", fake_stderr.getvalue())

    @patch("sleeper.cli.execute_sleep")
    def test_valid_duration_executes_sleep(self, mock_execute):
        exit_code = main(["--duration", "10"])
        self.assertEqual(exit_code, 0)
        mock_execute.assert_called_once_with(10.0, verbose=False)

    @patch("sleeper.cli.execute_sleep")
    def test_debug_output(self, mock_execute):
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main(["--debug", "--duration", "10"])
            self.assertEqual(exit_code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("--- Debug Information ---", output)
            self.assertIn("The --duration flag was used", output)
            mock_execute.assert_called_once()

    @patch("sleeper.cli.execute_sleep")
    def test_modular_sleep_debug_output(self, mock_execute):
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main(["--debug", "10"])
            self.assertEqual(exit_code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("--- Debug Information ---", output)
            self.assertIn("triggered modular sleep logic", output)
            mock_execute.assert_called_once()

    @patch("sleeper.cli.datetime")
    @patch("sleeper.cli.execute_sleep")
    def test_until_rollover_debug_output(self, mock_execute, mock_datetime):
        # Mock now to 14:00:00
        mock_datetime.now.return_value = datetime(2026, 10, 6, 14, 0, 0)
        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            exit_code = main(["--debug", "--until", "13:00"])
            self.assertEqual(exit_code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("--- Debug Information ---", output)
            self.assertIn("rolled over to tomorrow", output)
            mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
