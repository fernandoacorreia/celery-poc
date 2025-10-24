import argparse

from .utils import run_command


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add run command parser."""
    run_help = """Run the main application.

This command executes the main application using:
    uv run --dev python -m celery_poc.main
"""
    run_parser = subparsers.add_parser(
        "run",
        help="Run the main application",
        description=run_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run_parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> bool:
    """Run the main application."""
    return run_command("uv run --dev python -m celery_poc.main", "Main application")
