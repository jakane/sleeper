"""Command-line interface and argument parsing for sleeper."""

import argparse
import sys
from datetime import datetime

from sleeper import __version__
from sleeper.core import (
    calculate_modular_sleep,
    execute_sleep,
    parse_duration,
    parse_until,
)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for sleeper."""
    parser = argparse.ArgumentParser(
        prog="sleeper",
        description="Sleep for a specified duration or until a specified time.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit.",
    )

    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--until",
        type=str,
        help="Sleep until a specific time.\n"
             "Format: [[YYYY-mm-ddT]HH:MM[:SS]].\n"
             "Example: 10:30 (today or tomorrow) or 2025-12-25T15:00",
    )
    time_group.add_argument(
        "--duration",
        type=str,
        help="Sleep for a specified duration.\n"
             "Format: [[[DDT]HH:]MM:]SS.\n"
             "Example: 10 (10 seconds), 01:30 (1 minute 30 seconds), 1D01:00:00 (1 day, 1 hour)",
    )
    time_group.add_argument(
        "duration_positional",
        nargs="?",
        type=str,
        help="Sleep for a specified duration.\n"
             "Format: [[[HH:]MM:]SS].\n"
             "Example: 10 (10 seconds), 01:30 (1 minute 30 seconds), 300 (snap to 5m)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Provide progress notifications.")
    parser.add_argument("--debug", action="store_true", help="Explain how the sleep interval is decided.")

    return parser


def main(argv=None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.until and not args.duration and not args.duration_positional:
        parser.print_help()
        return 0

    now = datetime.now()
    target_datetime = None
    sleep_seconds = 0.0
    duration_str = None
    is_positional_and_bare = False

    try:
        if args.until:
            sleep_seconds, target_datetime = parse_until(args.until, now=now, auto_rollover=True)
        else:
            duration_str = args.duration if args.duration else args.duration_positional
            sleep_seconds = parse_duration(duration_str)

            # Modular sleep logic: applies only to bare, positional single-token arguments
            is_positional_and_bare = bool(
                args.duration_positional
                and not args.duration
                and duration_str
                and 'D' not in duration_str
                and ':' not in duration_str
            )
            if is_positional_and_bare and sleep_seconds > 0:
                module_value = sleep_seconds
                time_to_next = calculate_modular_sleep(module_value, now=now)

                if args.debug:
                    sub_sec = now.microsecond / 1_000_000
                    if module_value <= 60:
                        scale_name = "minute"
                        offset_val = now.second + sub_sec
                    elif module_value <= 3600:
                        scale_name = "hour"
                        offset_val = (now.minute * 60) + now.second + sub_sec
                    else:
                        scale_name = "day"
                        offset_val = (now.hour * 3600) + (now.minute * 60) + now.second + sub_sec

                    print("--- Debug Information ---")
                    print(f"The positional argument '{duration_str}' triggered modular sleep logic.")
                    print(f"The requested interval is {module_value:.2f} seconds.")
                    print(f"Current time in the {scale_name} is {offset_val:.3f} seconds.")
                    print(f"The initial sleep time of {sleep_seconds:.2f} seconds is being replaced.")
                    print(f"The calculated sleep time is {time_to_next:.3f} seconds to reach the next interval.")
                    print("-------------------------")

                sleep_seconds = time_to_next

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if sleep_seconds <= 0:
        if args.until:
            print("The specified --until time has already passed.", file=sys.stderr)
        else:
            print("Please specify a valid sleep duration or time.", file=sys.stderr)
        return 1

    if args.debug and not is_positional_and_bare:
        print("--- Debug Information ---")
        if args.until and target_datetime:
            print(f"The --until flag was used. The current time is {now.strftime('%Y-%m-%d %H:%M:%S')}.")
            print(f"The target time is {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}.")
            if target_datetime.date() > now.date():
                print("The target time was in the past for today; rolled over to tomorrow.")
            print(f"The sleep interval is calculated as the difference: {sleep_seconds:.2f} seconds.")
        else:
            source = "The --duration flag" if args.duration else "The positional argument"
            print(f"{source} was used. The input duration was {duration_str}.")
            print(f"This was parsed into a total sleep interval of {sleep_seconds:.2f} seconds.")
        print("-------------------------")

    try:
        execute_sleep(sleep_seconds, verbose=args.verbose)
    except KeyboardInterrupt:
        if args.verbose:
            sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.write("\nInterrupted.\n")
        sys.stdout.flush()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
