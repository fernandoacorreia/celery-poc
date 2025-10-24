"""
Celery Client Examples
Demonstrates various ways to call tasks and retrieve results
"""

import time
import logging
from celery import group, chain, chord
from celery.result import AsyncResult
from celery_poc.tasks import (
    app,
    add,
    multiply,
    process_data,
    download_file,
    risky_operation,
    parallel_task,
    process_step_1,
    process_step_2,
    process_step_3,
)
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# BASIC TASK CALLING
# ============================================================================


def example_basic_task():
    """
    Example 1: Basic task calling with .delay()
    """
    logger.info("=" * 60)
    logger.info("Example 1: Basic Task Calling")
    logger.info("=" * 60)

    # Send task asynchronously
    result = add.delay(4, 6)
    logger.info(f"Task sent with ID: {result.id}")

    # Wait for result
    logger.info("Waiting for result...")
    value = result.get(timeout=10)
    logger.info(f"Result: {value}")

    # Clean up
    result.forget()
    logger.info("Task completed and cleaned up\n")


# ============================================================================
# TASK WITH APPLY_ASYNC (More Control)
# ============================================================================


def example_apply_async():
    """
    Example 2: Using apply_async for more control
    """
    logger.info("=" * 60)
    logger.info("Example 2: Using apply_async()")
    logger.info("=" * 60)

    # Send task with options
    result = multiply.apply_async(
        args=[5, 3],
        countdown=2,  # Delay execution by 2 seconds
        expires=60,  # Task expires in 60 seconds
        retry=True,
        retry_policy={
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.2,
        },
    )

    logger.info(f"Task scheduled with ID: {result.id}")
    logger.info(f"Task state: {result.state}")

    # Wait for result
    value = result.get(timeout=10)
    logger.info(f"Result: {value}")
    result.forget()
    logger.info("Task completed\n")


# ============================================================================
# CHECKING TASK STATUS
# ============================================================================


def example_task_status():
    """
    Example 3: Checking task status without blocking
    """
    logger.info("=" * 60)
    logger.info("Example 3: Checking Task Status")
    logger.info("=" * 60)

    # Send long-running task
    result = process_data.delay(50)
    logger.info(f"Task sent with ID: {result.id}")

    # Poll for completion
    while not result.ready():
        state = result.state
        logger.info(f"Task state: {state}")

        if state == "PROGRESS":
            info = result.info
            logger.info(f"Progress: {info.get('percent', 0)}%")

        time.sleep(2)

    # Get final result
    final_result = result.get()
    logger.info(f"Final result: {final_result}")
    result.forget()
    logger.info("Task completed\n")


# ============================================================================
# ERROR HANDLING
# ============================================================================


def example_error_handling():
    """
    Example 4: Handling task errors
    """
    logger.info("=" * 60)
    logger.info("Example 4: Error Handling")
    logger.info("=" * 60)

    # Task that might fail
    result = risky_operation.delay("OP-12345")
    logger.info(f"Task sent with ID: {result.id}")

    try:
        # Wait for result with timeout
        value = result.get(timeout=10, propagate=True)
        logger.info(f"Task succeeded: {value}")
    except Exception as exc:
        logger.error(f"Task failed with error: {exc}")
        logger.error(f"Traceback: {result.traceback}")
    finally:
        result.forget()

    logger.info("Error handling example completed\n")


# ============================================================================
# RETRIEVING TASK BY ID
# ============================================================================


def example_retrieve_by_id():
    """
    Example 5: Retrieving task result by ID
    """
    logger.info("=" * 60)
    logger.info("Example 5: Retrieving Task by ID")
    logger.info("=" * 60)

    # Send task
    result = add.delay(10, 20)
    task_id = result.id
    logger.info(f"Task sent with ID: {task_id}")

    # Simulate storing task_id and retrieving later
    # In real application, you might store this in a database
    time.sleep(2)

    # Retrieve task by ID
    retrieved_result = AsyncResult(task_id, app=app)
    logger.info(f"Retrieved task state: {retrieved_result.state}")

    if retrieved_result.ready():
        value = retrieved_result.get()
        logger.info(f"Task result: {value}")

    retrieved_result.forget()
    logger.info("Retrieval example completed\n")


# ============================================================================
# TASK CHAINS
# ============================================================================


def example_task_chain():
    """
    Example 6: Chaining tasks (pipeline)
    """
    logger.info("=" * 60)
    logger.info("Example 6: Task Chains")
    logger.info("=" * 60)

    # Create a chain: step1 | step2 | step3
    workflow = chain(process_step_1.s(5), process_step_2.s(), process_step_3.s())

    # Execute chain
    result = workflow.apply_async()
    logger.info(f"Chain started with ID: {result.id}")

    # Wait for final result
    final_result = result.get(timeout=30)
    logger.info(f"Chain completed with result: {final_result}")
    result.forget()
    logger.info("Chain example completed\n")


# ============================================================================
# TASK GROUPS (Parallel Execution)
# ============================================================================


def example_task_group():
    """
    Example 7: Running tasks in parallel using group
    """
    logger.info("=" * 60)
    logger.info("Example 7: Task Groups (Parallel)")
    logger.info("=" * 60)

    # Create group of parallel tasks
    job = group(
        [
            parallel_task.s(1),
            parallel_task.s(2),
            parallel_task.s(3),
            parallel_task.s(4),
            parallel_task.s(5),
        ]
    )

    # Execute group
    result = job.apply_async()
    logger.info(f"Group started with ID: {result.id}")

    # Wait for all tasks to complete
    results = result.get(timeout=30)
    logger.info(f"All tasks completed: {results}")
    result.forget()
    logger.info("Group example completed\n")


# ============================================================================
# TASK CHORD (Group + Callback)
# ============================================================================


def example_task_chord():
    """
    Example 8: Using chord (group with callback)
    """
    logger.info("=" * 60)
    logger.info("Example 8: Task Chord")
    logger.info("=" * 60)

    # Create chord: parallel tasks + callback
    callback = add.s()  # This will receive list of results
    job = chord([multiply.s(2, 2), multiply.s(3, 3), multiply.s(4, 4)])(callback)

    logger.info(f"Chord started with ID: {job.id}")

    # Wait for callback result
    result = job.get(timeout=30)
    logger.info(f"Chord callback result: {result}")
    job.forget()
    logger.info("Chord example completed\n")


# ============================================================================
# CUSTOM STATE HANDLING
# ============================================================================


def example_custom_state():
    """
    Example 9: Handling custom task states
    """
    logger.info("=" * 60)
    logger.info("Example 9: Custom Task States")
    logger.info("=" * 60)

    # Send task with custom states
    result = download_file.delay("https://example.com/file.zip")
    logger.info(f"Download task sent with ID: {result.id}")

    # Monitor custom state
    while not result.ready():
        state = result.state
        logger.info(f"Current state: {state}")

        if state == "DOWNLOADING":
            info = result.info
            progress = info.get("progress", 0)
            logger.info(f"Download progress: {progress}%")

        time.sleep(1)

    # Get final result
    final_result = result.get()
    logger.info(f"Download completed: {final_result}")
    result.forget()
    logger.info("Custom state example completed\n")


# ============================================================================
# TIMEOUT HANDLING
# ============================================================================


def example_timeout():
    """
    Example 10: Handling task timeouts
    """
    logger.info("=" * 60)
    logger.info("Example 10: Timeout Handling")
    logger.info("=" * 60)

    # Send long-running task
    result = process_data.delay(100)
    logger.info(f"Task sent with ID: {result.id}")

    try:
        # Wait with short timeout (will timeout)
        value = result.get(timeout=2)
        logger.info(f"Task completed: {value}")
    except TimeoutError:
        logger.warning("Task timed out, but continues running in background")
        logger.info(f"Task state: {result.state}")

        # You can check later or revoke
        # result.revoke(terminate=True)  # Forcefully stop task
    finally:
        result.forget()

    logger.info("Timeout example completed\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """
    Run all examples
    """

    load_dotenv()

    logger.info("\n" + "=" * 60)
    logger.info("CELERY CLIENT EXAMPLES")
    logger.info("=" * 60 + "\n")

    examples = [
        ("Basic Task", example_basic_task),
        ("Apply Async", example_apply_async),
        ("Task Status", example_task_status),
        ("Error Handling", example_error_handling),
        ("Retrieve by ID", example_retrieve_by_id),
        ("Task Chain", example_task_chain),
        ("Task Group", example_task_group),
        ("Task Chord", example_task_chord),
        ("Custom State", example_custom_state),
        ("Timeout", example_timeout),
    ]

    for name, example_func in examples:
        try:
            logger.info(f"\nRunning: {name}")
            example_func()
            time.sleep(1)  # Brief pause between examples
        except Exception as exc:
            logger.error(f"Example '{name}' failed: {exc}")

    logger.info("\n" + "=" * 60)
    logger.info("ALL EXAMPLES COMPLETED")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
