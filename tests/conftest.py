"""Configuration file for pytest tests.

This file contains shared fixtures and configuration that can be used
across all test files in the tests directory.
"""

import pytest
import tempfile
from pathlib import Path
from contextlib import contextmanager


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory as a Path instance."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory that is automatically cleaned up after the test passes.

    Usage example:
        def test_file_operations(temp_dir):
            with temp_dir() as temp_path:
                # Create files in the temporary directory
                (temp_path / "test.txt").write_text("Hello, World!")
                # Directory will be automatically deleted when exiting the context
    """

    @contextmanager
    def _temp_dir():
        with tempfile.TemporaryDirectory() as temp_path_str:
            yield Path(temp_path_str)

    return _temp_dir
