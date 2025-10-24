import argparse

from .utils import run_command


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add build command parser."""
    build_help = """Build the wheel file.

This command builds a wheel distribution file using:
    uv build
    
The wheel file will be created in the 'dist/' directory.
"""
    build_parser = subparsers.add_parser(
        "build",
        help="Build the wheel file",
        description=build_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build_parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> bool:
    """Build the wheel file."""
    return run_command("uv build", "Building wheel file")
