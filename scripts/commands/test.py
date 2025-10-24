import argparse

from .utils import run_command


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add test command parser."""
    test_help = """Run tests using pytest.

This command runs pytest with any additional arguments passed verbatim.
Examples:
    dev test                    # Run all tests
    dev test tests/test_main.py # Run specific test file
    dev test -v                 # Run with verbose output
    dev test --cov              # Run with coverage report
    dev test --cov=src          # Run with coverage for specific path
    dev test --cov --cov-report=html  # Generate HTML coverage report
    dev test -k test_function   # Run tests matching pattern
"""
    test_parser = subparsers.add_parser(
        "test",
        help="Run tests using pytest",
        description=test_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    test_parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> bool:
    """Run tests using pytest."""
    # Build the pytest command
    cmd_parts = ["uv", "run", "--dev", "-m", "pytest"]

    # Add any unknown arguments (extra args passed to pytest)
    if hasattr(args, "unknown_args") and args.unknown_args:
        cmd_parts.extend(args.unknown_args)

    cmd = " ".join(cmd_parts)

    return run_command(cmd, "pytest")
