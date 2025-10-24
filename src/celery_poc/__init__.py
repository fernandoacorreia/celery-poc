"""
Celery POC Package
Main package exposing Celery app and tasks for easy importing
"""

from celery_poc.tasks import (
    app,
    add,
    multiply,
    divide,
    process_data,
    download_file,
    risky_operation,
    parallel_task,
    process_step_1,
    process_step_2,
    process_step_3,
    cleanup_old_data,
)

__all__ = [
    "app",
    "add",
    "multiply",
    "divide",
    "process_data",
    "download_file",
    "risky_operation",
    "parallel_task",
    "process_step_1",
    "process_step_2",
    "process_step_3",
    "cleanup_old_data",
]
