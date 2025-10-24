import argparse

from .utils import run_command


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add lint command parser."""
    lint_help = """Run linting tools (black, ruff, mypy).

This command runs code formatting and linting tools in sequence:
    • Black: Code formatter (uv run --dev -m black .)
    • Ruff: Linter with auto-fix (uv run --dev -m ruff check --fix .)
    • MyPy: Type checker (uv run --dev -m mypy .) - if available
"""
    lint_parser = subparsers.add_parser(
        "lint",
        help="Run linting tools (black, ruff, mypy)",
        description=lint_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    lint_parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> bool:
    """Run linting tools (black, ruff, mypy)."""
    print("Running linting tools...")

    results = [
        run_command("uv run --dev -m black .", "Black formatter"),
        run_command("uv run --dev -m ruff check --fix .", "Ruff linter"),
        run_command("uv run --dev -m mypy .", "MyPy type checker"),
    ]
    return all(results)
