# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that demonstrates best practices for Python 3.12 projects. It uses `uv` as the package manager and includes a custom development CLI (`./dev`) for common tasks.

## Development Commands

All development tasks are accessed through the `./dev` script:

```bash
# Run the application
./dev run

# Run all tests
./dev test

# Run specific test file
./dev test tests/test_main.py

# Run tests with coverage
./dev test --cov

# Run tests with HTML coverage report
./dev test --cov --cov-report=html

# Run tests matching a pattern
./dev test -k test_function

# Run linting (black, ruff, mypy)
./dev lint

# Build wheel distribution
./dev build

# Run Claude CLI (if available)
./dev claude [args]
```

## Architecture

### Custom Development CLI (`scripts/dev.py`)

The `./dev` script is a bash wrapper that executes `scripts/dev.py`, which uses a plugin-style architecture:

- **Command modules**: Each command is a separate module in `scripts/commands/` with:
  - `add_parser()` function to register the command with argparse
  - `execute()` function that runs the command
- **Main script**: `scripts/dev.py` discovers and registers all command modules
- **Unknown arguments**: The `test` and `claude` commands accept and forward unknown arguments to their underlying tools

To add a new command:
1. Create a new module in `scripts/commands/`
2. Implement `add_parser(subparsers)` and `execute(args)` functions
3. Import and register it in `scripts/dev.py`

### Main Application (`src/celery_poc/main.py`)

The main application demonstrates:
- **Environment-based configuration**: Uses `python-dotenv` to load `.env` file
- **Configurable logging**: Supports two formats via `LOG_FORMAT` env var:
  - `pretty`: Human-readable format (default)
  - `json`: Structured JSON logging via custom `JSONFormatter`
- **Utility functions**: Common file operations (read, write, copy, create directories, list files)

### Test Infrastructure (`tests/`)

Uses pytest with custom fixtures defined in `conftest.py`:
- `test_data_dir`: Returns `Path` to `tests/data/` directory
- `temp_dir`: Context manager that creates and cleans up temporary directories

Example usage:
```python
def test_example(temp_dir, test_data_dir):
    with temp_dir() as tmp_path:
        # tmp_path is a Path object to a temporary directory
        # automatically cleaned up after the test
        pass
```

## Configuration

- **Package metadata**: `pyproject.toml` (Python 3.12 required)
- **Environment variables**: Copy `example.env` to `.env` and customize
- **Type checking**: Strict mode for `src/`, relaxed for `tests/` (see `tool.mypy` in `pyproject.toml`)
- **Dependencies**:
  - Runtime: pydantic, python-dotenv
  - Dev: black, ruff, mypy, pytest, pytest-cov
