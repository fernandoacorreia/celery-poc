"""
Task Definitions
Contains all Celery task functions following best practices
"""
import time
import logging
from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery('celery_poc')
app.config_from_object('celery_poc.celeryconfig')


# ============================================================================
# BASE TASK CLASS (Optional: for custom behavior)
# ============================================================================

class CallbackTask(Task):
    """
    Custom task class that can execute callbacks on success/failure
    """
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f"Task {task_id} succeeded with result: {retval}")
        return super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f"Task {task_id} failed with error: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)


# ============================================================================
# SIMPLE TASKS
# ============================================================================

@app.task(name='celery_poc.tasks.add', bind=False)
def add(x, y):
    """
    Simple addition task - demonstrates basic task definition

    Args:
        x (int): First number
        y (int): Second number

    Returns:
        int: Sum of x and y
    """
    logger.info(f"Adding {x} + {y}")
    result = x + y
    logger.info(f"Result: {result}")
    return result


@app.task(name='celery_poc.tasks.multiply', bind=False)
def multiply(x, y):
    """
    Simple multiplication task

    Args:
        x (int): First number
        y (int): Second number

    Returns:
        int: Product of x and y
    """
    logger.info(f"Multiplying {x} * {y}")
    return x * y


# ============================================================================
# TASK WITH RETRY LOGIC
# ============================================================================

@app.task(
    name='celery_poc.tasks.divide',
    bind=True,
    autoretry_for=(ZeroDivisionError,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def divide(self, x, y):
    """
    Division task with automatic retry on ZeroDivisionError

    Args:
        self: Task instance (bind=True required)
        x (float): Numerator
        y (float): Denominator

    Returns:
        float: Result of division

    Raises:
        ZeroDivisionError: If y is zero (will auto-retry)
    """
    try:
        logger.info(f"Dividing {x} / {y}")
        result = x / y
        return result
    except ZeroDivisionError as exc:
        logger.warning(f"Attempt {self.request.retries + 1} failed: Division by zero")
        raise


# ============================================================================
# LONG-RUNNING TASK
# ============================================================================

@app.task(
    name='celery_poc.tasks.process_data',
    bind=True,
    time_limit=120,  # Hard time limit (2 minutes)
    soft_time_limit=100  # Soft time limit (100 seconds)
)
def process_data(self, data_size):
    """
    Simulates a long-running data processing task
    Demonstrates time limits and progress reporting

    Args:
        self: Task instance
        data_size (int): Amount of data to process

    Returns:
        dict: Processing results
    """
    try:
        logger.info(f"Starting to process {data_size} items")

        processed = 0
        for i in range(data_size):
            # Simulate processing
            time.sleep(0.1)
            processed += 1

            # Update task state with progress
            if i % 10 == 0:
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed,
                        'total': data_size,
                        'percent': int((processed / data_size) * 100)
                    }
                )

        result = {
            'status': 'completed',
            'processed': processed,
            'total': data_size
        }
        logger.info(f"Completed processing {processed} items")
        return result

    except SoftTimeLimitExceeded:
        logger.warning("Task exceeded soft time limit, cleaning up...")
        # Perform cleanup
        return {
            'status': 'timeout',
            'processed': processed,
            'total': data_size
        }


# ============================================================================
# TASK WITH CUSTOM STATE
# ============================================================================

@app.task(name='celery_poc.tasks.download_file', bind=True)
def download_file(self, url):
    """
    Simulates file download with custom state updates

    Args:
        self: Task instance
        url (str): URL to download

    Returns:
        dict: Download results
    """
    logger.info(f"Starting download from {url}")

    # Update state to custom 'DOWNLOADING'
    self.update_state(
        state='DOWNLOADING',
        meta={'url': url, 'progress': 0}
    )

    # Simulate download progress
    for progress in range(0, 101, 20):
        time.sleep(0.5)
        self.update_state(
            state='DOWNLOADING',
            meta={'url': url, 'progress': progress}
        )

    logger.info(f"Download completed: {url}")
    return {'url': url, 'status': 'completed', 'size': 1024000}


# ============================================================================
# TASK WITH ERROR HANDLING
# ============================================================================

@app.task(name='celery_poc.tasks.risky_operation', bind=True, base=CallbackTask)
def risky_operation(self, operation_id):
    """
    Task that demonstrates comprehensive error handling
    Uses custom CallbackTask base class

    Args:
        self: Task instance
        operation_id (str): Operation identifier

    Returns:
        dict: Operation results
    """
    logger.info(f"Starting risky operation: {operation_id}")

    try:
        # Simulate operation that might fail
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise ValueError(f"Operation {operation_id} encountered an error")

        time.sleep(2)

        result = {
            'operation_id': operation_id,
            'status': 'success',
            'timestamp': time.time()
        }
        return result

    except ValueError as exc:
        logger.error(f"Operation {operation_id} failed: {exc}")
        # Don't retry ValueError
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in operation {operation_id}: {exc}")
        # Retry unexpected errors
        raise self.retry(exc=exc, countdown=10, max_retries=2)


# ============================================================================
# CHAINED TASKS EXAMPLE
# ============================================================================

@app.task(name='celery_poc.tasks.process_step_1')
def process_step_1(data):
    """First step in a processing chain"""
    logger.info(f"Step 1: Processing {data}")
    return {'step': 1, 'data': data, 'result': data * 2}


@app.task(name='celery_poc.tasks.process_step_2')
def process_step_2(previous_result):
    """Second step in a processing chain"""
    logger.info(f"Step 2: Processing {previous_result}")
    data = previous_result['result']
    return {'step': 2, 'data': data, 'result': data + 10}


@app.task(name='celery_poc.tasks.process_step_3')
def process_step_3(previous_result):
    """Final step in a processing chain"""
    logger.info(f"Step 3: Processing {previous_result}")
    data = previous_result['result']
    return {'step': 3, 'final_result': data * 3}


# ============================================================================
# PERIODIC TASK EXAMPLE (Requires celery beat)
# ============================================================================

@app.task(name='celery_poc.tasks.cleanup_old_data')
def cleanup_old_data():
    """
    Periodic task to clean up old data
    Schedule this in celeryconfig.py using beat_schedule
    """
    logger.info("Running periodic cleanup task")
    # Cleanup logic here
    cleaned = 42  # Simulated cleanup count
    logger.info(f"Cleaned up {cleaned} items")
    return {'cleaned': cleaned}


# ============================================================================
# GROUP TASK EXAMPLE
# ============================================================================

@app.task(name='celery_poc.tasks.parallel_task')
def parallel_task(item_id):
    """
    Task designed to be run in parallel groups

    Args:
        item_id (int): Item identifier

    Returns:
        dict: Processing result
    """
    logger.info(f"Processing item {item_id}")
    time.sleep(1)  # Simulate work
    return {'item_id': item_id, 'processed': True}
