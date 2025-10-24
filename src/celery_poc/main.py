import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for log messages."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def configure_logging() -> None:
    """Configure logging based on environment variables."""
    # Load environment variables from .env file
    load_dotenv()

    # Get log level from environment, default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Get log format from environment, default to pretty
    log_format = os.getenv("LOG_FORMAT", "pretty").lower()

    # Configure logging format based on log_format
    if log_format == "json":
        formatter = JSONFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        format_string = ""  # Will be overridden by JSONFormatter
    elif log_format == "pretty":
        formatter = None
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        raise ValueError(
            f"Invalid LOG_FORMAT '{log_format}'. Must be 'json' or 'pretty'"
        )

    # Configure logging
    logging.basicConfig(
        level=numeric_level, format=format_string, datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Apply JSON formatter if needed
    if formatter:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}, format: {log_format}")


def greetings(name: str = "World") -> str:
    return f"Hello, {name}!"


def read_file_content(file_path: Path) -> str:
    """Read content from a file."""
    return file_path.read_text()


def write_file_content(file_path: Path, content: str) -> None:
    """Write content to a file."""
    file_path.write_text(content)


def create_directory(dir_path: Path) -> None:
    """Create a directory if it doesn't exist."""
    dir_path.mkdir(parents=True, exist_ok=True)


def list_files_in_directory(dir_path: Path) -> list[Path]:
    """List all files in a directory."""
    return [f for f in dir_path.iterdir() if f.is_file()]


def copy_file(source_path: Path, destination_path: Path) -> None:
    """Copy a file from source to destination."""
    destination_path.write_text(source_path.read_text())


def main() -> None:
    """Hello world main function."""
    # Configure logging first
    configure_logging()

    # Get logger for this module
    logger = logging.getLogger(__name__)

    # Log some messages to demonstrate the logging configuration
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Print greeting
    greeting = greetings()
    print(greeting)
    logger.info(f"Greeting: {greeting}")


if __name__ == "__main__":
    main()
