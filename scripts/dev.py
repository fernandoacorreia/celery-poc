import argparse
import sys

from commands import build, claude, lint, run, test


def _prepare_parser() -> argparse.ArgumentParser:
    """Prepare and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Development helper script",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add commands in alphabetical order
    build.add_parser(subparsers)
    claude.add_parser(subparsers)
    lint.add_parser(subparsers)
    run.add_parser(subparsers)
    test.add_parser(subparsers)

    return parser


def _execute_command(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Execute the command based on parsed arguments."""
    if not args.command:
        parser.print_help()
        sys.exit(0)

    success = args.func(args)
    sys.exit(0 if success else 1)


def main() -> None:
    """Main entry point for dev script."""
    parser = _prepare_parser()
    args, unknown = parser.parse_known_args()

    # Pass unknown args to any command that needs them
    if unknown:
        args.unknown_args = unknown

    _execute_command(parser, args)


if __name__ == "__main__":
    main()
