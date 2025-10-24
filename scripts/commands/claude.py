import argparse

from .utils import run_command


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add claude command parser."""
    claude_help = """Run Claude CLI with additional arguments.

This command executes the Claude CLI using:
    uv run claude [additional arguments]

Any additional arguments passed to this command will be forwarded to the Claude CLI.
"""
    claude_parser = subparsers.add_parser(
        "claude",
        help="Run Claude CLI with additional arguments",
        description=claude_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    claude_parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> bool:
    """Run Claude CLI with additional arguments."""
    # Build the command with additional arguments
    cmd_parts = ["uv run claude"]

    # Use unknown_args if available (passed from main dev script)
    if hasattr(args, "unknown_args") and args.unknown_args:
        cmd_parts.extend(args.unknown_args)

    cmd = " ".join(cmd_parts)
    return run_command(cmd, "Claude CLI")
