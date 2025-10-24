# Celery + Redis Proof of Concept - Detailed Plan

## Table of Contents
1. [Overview](#overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Design](#component-design)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Design Decisions](#design-decisions)
7. [Implementation Details](#implementation-details)
8. [Code Snippets](#code-snippets)
9. [Deployment Strategy](#deployment-strategy)
10. [Testing Approach](#testing-approach)
11. [Monitoring & Observability](#monitoring--observability)
12. [Security Considerations](#security-considerations)
13. [Scalability & Performance](#scalability--performance)
14. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview

### Purpose
This proof of concept demonstrates a production-ready implementation of Celery with Redis as both the message broker and result backend. The goal is to showcase asynchronous task processing in a simple, minimalistic, yet comprehensive manner.

### Key Objectives
- ✅ Demonstrate asynchronous task execution
- ✅ Show proper separation of concerns
- ✅ Implement best practices from Celery documentation
- ✅ Provide containerized environment for easy deployment
- ✅ Enable monitoring and observability
- ✅ Follow 12-factor app principles

### Target Audience
- Developers new to Celery
- Teams evaluating distributed task processing solutions
- Engineers looking for a reference implementation

---

## High-Level Architecture

### Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT APPLICATION                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  client.py - Sends tasks to the queue                     │  │
│  │  • Creates Celery app instance                            │  │
│  │  • Calls tasks using .delay() or .apply_async()           │  │
│  │  • Retrieves results using AsyncResult                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ (1) Send Task
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MESSAGE BROKER (Redis)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Queue Management: Stores task messages                 │  │
│  │  • Pub/Sub: Events and monitoring                         │  │
│  │  • Persistence: Task queue on disk (AOF/RDB)              │  │
│  │  • Port: 6379                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ (2) Fetch Task
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CELERY WORKER(S)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  worker process - Executes tasks                          │  │
│  │  • Monitors queue for new tasks                           │  │
│  │  • Executes task functions                                │  │
│  │  • Handles failures and retries                           │  │
│  │  • Updates task state                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ (3) Store Result
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESULT BACKEND (Redis)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Stores task results and states                         │  │
│  │  • TTL-based expiration for cleanup                       │  │
│  │  • Accessible by task ID                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ (4) Retrieve Result
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT APPLICATION                        │
│  (Retrieves result using AsyncResult.get())                     │
└─────────────────────────────────────────────────────────────────┘

Required Monitoring:
┌─────────────────────────────────────────────────────────────────┐
│                      FLOWER (Web UI)                            │
│  • Real-time task monitoring                                    │
│  • Worker management                                            │
│  • Task statistics and history                                 │
│  • Port: 5555                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Task Creation**: Client creates a task and sends it to Redis broker
2. **Task Queuing**: Redis stores the task message in a queue
3. **Task Fetching**: Worker polls Redis and fetches the task
4. **Task Execution**: Worker executes the task function
5. **Result Storage**: Worker stores the result back in Redis
6. **Result Retrieval**: Client retrieves the result using the task ID

### Component Interaction

```
CLIENT          BROKER (Redis)       WORKER          BACKEND (Redis)
  |                   |                 |                    |
  |-- send task ----->|                 |                    |
  |                   |<-- poll task ---|                    |
  |                   |                 |-- execute -------->|
  |                   |                 |                    |
  |                   |                 |<-- store result ---|
  |<-- get result ----|-----------------|                    |
  |                   |                 |                    |
```

---

## Component Design

### 1. Tasks Module (`tasks.py`)

**Responsibilities:**
- Define all task functions
- Configure Celery application
- Set task-specific options (retries, rate limits, etc.)

**Design Principles:**
- Pure functions when possible (no side effects)
- Idempotent operations (safe to retry)
- Clear naming conventions
- Proper error handling

### 2. Worker (`worker.py` or CLI)

**Responsibilities:**
- Initialize Celery worker process
- Load task modules
- Handle task execution lifecycle
- Manage worker health and state

**Design Principles:**
- Graceful shutdown handling
- Resource cleanup
- Logging and monitoring
- Configurable concurrency

### 3. Client (`client.py`)

**Responsibilities:**
- Demonstrate task invocation patterns
- Show result retrieval methods
- Handle task states and errors
- Provide usage examples

**Design Principles:**
- Clear demonstration of API usage
- Proper error handling
- Timeout management
- Resource cleanup (call .forget() or .get())

### 4. Docker Compose (`docker-compose.yml`)

**Responsibilities:**
- Orchestrate service containers
- Configure networking
- Manage dependencies
- Provide development environment

**Design Principles:**
- Environment isolation
- Easy startup/teardown
- Volume management for persistence
- Health checks

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Task Queue | Celery | 5.5.x | Distributed task processing |
| Message Broker | Redis | 7.x | Message transport and storage |
| Result Backend | Redis | 7.x | Task result storage |
| Language | Python | 3.12 | Application development |
| Package Manager | uv | Latest | Fast Python package installer |
| Containerization | Docker | Latest | Environment isolation |
| Orchestration | Docker Compose | Latest | Multi-container management |
| Monitoring | Flower | 2.x | Web-based monitoring (required) |

### Python Dependencies

Added to `pyproject.toml`:
```toml
dependencies = [
    "celery[redis]",
    "redis",
    "flower",
    "pydantic",
    "python-dotenv",
]
```

---

## Project Structure

```
celery-poc/
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Python 3.12 + uv image
├── .dockerignore              # Docker build exclusions
├── pyproject.toml             # Dependencies (includes celery[redis], flower)
├── uv.lock                    # Locked dependencies
├── .env                       # Environment variables
├── example.env                # Environment variable template
├── .gitignore                 # Git ignore patterns
│
├── src/celery_poc/            # Main application code
│   ├── __init__.py
│   ├── main.py               # Existing main application
│   ├── tasks.py              # Celery task definitions
│   ├── celeryconfig.py       # Celery configuration
│   └── client.py             # Task caller examples
│
├── scripts/                   # Development CLI
│   ├── dev.py                # Main dev script
│   └── commands/             # Command modules
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_main.py          # Main app tests
│   ├── test_tasks.py         # Celery task tests
│   └── test_integration.py   # Integration tests
│
├── logs/                      # Application logs (Docker volume)
│
└── plans/                     # Documentation
    └── INITIAL_PLAN.md       # This file
```

---

## Design Decisions

### 1. Why Redis for Both Broker and Backend?

**Decision:** Use Redis as both message broker and result backend

**Rationale:**
- **Simplicity**: Single dependency reduces operational complexity
- **Performance**: Redis is extremely fast for both roles
- **Development**: Perfect for POC and development environments
- **Documentation**: Most commonly documented configuration in Celery

**Trade-offs:**
- Redis is in-memory; consider persistence configuration for production
- For critical production workloads, RabbitMQ + Redis might be better
- Memory limits must be monitored for large result sets

### 2. Serialization Format: JSON

**Decision:** Use JSON for task and result serialization

**Rationale:**
- **Security**: Unlike pickle, JSON doesn't execute arbitrary code
- **Debugging**: Human-readable format
- **Interoperability**: Works across different languages
- **Celery Recommendation**: Explicitly recommended in security documentation

**Configuration:**
```python
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
```

### 3. Task Design Pattern

**Decision:** Use function-based tasks with `@app.task` decorator

**Rationale:**
- **Simplicity**: Easy to understand for POC
- **Best Practice**: Recommended by Celery documentation
- **Flexibility**: Can be extended to class-based tasks later

**Pattern:**
```python
@app.task(bind=True, name='tasks.example')
def example_task(self, arg1, arg2):
    # Task logic
    return result
```

### 4. Configuration Management

**Decision:** Use dedicated `celeryconfig.py` module

**Rationale:**
- **Separation**: Keeps configuration separate from code
- **Centralization**: All settings in one place
- **Best Practice**: Recommended by Celery documentation
- **Maintainability**: Easy to modify without touching task code

### 5. Docker Compose Over Kubernetes

**Decision:** Use Docker Compose for POC deployment

**Rationale:**
- **Simplicity**: Lower learning curve
- **Development**: Perfect for local development and POC
- **Portability**: Works on any machine with Docker
- **Quick Setup**: Single command to start everything

### 6. Worker Concurrency Model

**Decision:** Use prefork (multiprocessing) as default

**Rationale:**
- **Default**: Celery's default concurrency model
- **CPU-Bound**: Good for compute-intensive tasks
- **Stability**: Most mature and well-tested
- **Simplicity**: No additional dependencies

**Alternative Options:**
- `eventlet`: For I/O-bound tasks
- `gevent`: For I/O-bound tasks
- `threads`: For I/O-bound tasks with threading
- `solo`: For debugging (single-threaded)

---

## Implementation Details

### Application Initialization Pattern

The Celery application should be initialized once and imported everywhere:

```python
# src/celery_poc/tasks.py - Single point of initialization
from celery import Celery

app = Celery('celery_poc')
app.config_from_object('celery_poc.celeryconfig')

# Now define tasks
@app.task
def my_task():
    pass
```

### Task Naming Convention

Follow a clear naming convention for tasks:

- **Pattern**: `module.function_name`
- **Example**: `celery_poc.tasks.process_data`, `celery_poc.tasks.send_email`
- **Explicit Naming**: Use `name` parameter for clarity

```python
@app.task(name='celery_poc.tasks.process_data')
def process_data(data):
    pass
```

### Error Handling Strategy

Implement comprehensive error handling:

```python
@app.task(bind=True, autoretry_for=(Exception,), 
          retry_kwargs={'max_retries': 3, 'countdown': 5})
def resilient_task(self, arg):
    try:
        # Task logic
        result = process(arg)
        return result
    except SpecificError as exc:
        # Log and re-raise for retry
        logger.error(f"Task failed: {exc}")
        raise
```

### Result Management

Always clean up results to prevent memory leaks:

```python
# Good: Retrieve and forget
result = task.delay(arg)
value = result.get(timeout=10)
result.forget()  # Clean up

# Better: Use context manager pattern
def safe_task_call(task, *args, **kwargs):
    result = task.delay(*args, **kwargs)
    try:
        return result.get(timeout=10)
    finally:
        result.forget()
```

---

## Code Snippets

### 1. Core Celery Configuration (`celeryconfig.py`)

```python
"""
Celery Configuration Module
Following Celery 5.x best practices and recommendations
"""
from kombu import Exchange, Queue

# ============================================================================
# BROKER SETTINGS
# ============================================================================

# Redis as message broker
broker_url = 'redis://redis:6379/0'

# Broker connection retry on startup
broker_connection_retry_on_startup = True

# Broker connection retry
broker_connection_retry = True
broker_connection_max_retries = 10

# ============================================================================
# RESULT BACKEND SETTINGS
# ============================================================================

# Redis as result backend
result_backend = 'redis://redis:6379/1'

# Result expiration time (24 hours)
result_expires = 86400

# Store task metadata (args, kwargs, etc.)
result_extended = True

# ============================================================================
# SERIALIZATION SETTINGS
# ============================================================================

# Use JSON for security (no arbitrary code execution like pickle)
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# ============================================================================
# TIMEZONE SETTINGS
# ============================================================================

# Enable UTC
enable_utc = True
timezone = 'UTC'

# ============================================================================
# TASK EXECUTION SETTINGS
# ============================================================================

# Don't send events for each task (reduce overhead)
# Enable only if using monitoring tools like Flower
task_send_sent_event = True

# Track started state
task_track_started = True

# Acknowledge tasks after completion (not before)
task_acks_late = True

# Reject task on worker timeout
task_reject_on_worker_lost = True

# ============================================================================
# WORKER SETTINGS
# ============================================================================

# Worker prefetch multiplier (how many tasks to prefetch)
# Lower value = better load balancing, higher value = better throughput
worker_prefetch_multiplier = 4

# Maximum tasks per worker child process before restart
# Helps prevent memory leaks
worker_max_tasks_per_child = 1000

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Worker log format
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# ============================================================================
# QUEUE CONFIGURATION
# ============================================================================

# Define task routing
task_routes = {
    'celery_poc.tasks.quick_task': {'queue': 'quick'},
    'celery_poc.tasks.slow_task': {'queue': 'slow'},
}

# Default queue
task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'

# Define queues explicitly
task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('quick', Exchange('quick'), routing_key='quick'),
    Queue('slow', Exchange('slow'), routing_key='slow'),
)

# ============================================================================
# TASK ANNOTATIONS (Per-task settings)
# ============================================================================

task_annotations = {
    'celery_poc.tasks.slow_task': {
        'rate_limit': '10/m',  # 10 tasks per minute
        'time_limit': 300,     # Hard time limit (5 minutes)
        'soft_time_limit': 240,  # Soft time limit (4 minutes)
    },
}
```

### 2. Task Definitions (`tasks.py`)

```python
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
```

### 3. Client Usage Examples (`client.py`)

```python
"""
Celery Client Examples
Demonstrates various ways to call tasks and retrieve results
"""
import time
import logging
from celery import group, chain, chord
from celery.result import AsyncResult
from celery_poc.tasks import (
    app, add, multiply, divide, process_data,
    download_file, risky_operation, parallel_task,
    process_step_1, process_step_2, process_step_3
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
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
        expires=60,   # Task expires in 60 seconds
        retry=True,
        retry_policy={
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
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
        
        if state == 'PROGRESS':
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
    result = risky_operation.delay('OP-12345')
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
    workflow = chain(
        process_step_1.s(5),
        process_step_2.s(),
        process_step_3.s()
    )
    
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
    job = group([
        parallel_task.s(1),
        parallel_task.s(2),
        parallel_task.s(3),
        parallel_task.s(4),
        parallel_task.s(5)
    ])
    
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
    job = chord([
        multiply.s(2, 2),
        multiply.s(3, 3),
        multiply.s(4, 4)
    ])(callback)
    
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
    result = download_file.delay('https://example.com/file.zip')
    logger.info(f"Download task sent with ID: {result.id}")
    
    # Monitor custom state
    while not result.ready():
        state = result.state
        logger.info(f"Current state: {state}")
        
        if state == 'DOWNLOADING':
            info = result.info
            progress = info.get('progress', 0)
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


if __name__ == '__main__':
    main()
```

### 4. Docker Compose Configuration (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  # ============================================================================
  # Redis Service (Broker + Backend)
  # ============================================================================
  redis:
    image: redis:7-alpine
    container_name: celery-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - celery-network
    restart: unless-stopped

  # ============================================================================
  # Celery Worker Service
  # ============================================================================
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: celery-worker
    command: uv run celery -A celery_poc.tasks worker --loglevel=info --concurrency=4
    volumes:
      - ./src:/app/src
      - ./logs:/logs
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - celery-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 512M

  # ============================================================================
  # Flower Monitoring Service (Required for this POC)
  # ============================================================================
  flower:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: celery-flower
    command: uv run celery -A celery_poc.tasks flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - worker
    networks:
      - celery-network
    restart: unless-stopped

# ============================================================================
# Networks
# ============================================================================
networks:
  celery-network:
    driver: bridge

# ============================================================================
# Volumes
# ============================================================================
volumes:
  redis_data:
    driver: local
```

### 5. Dockerfile

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies using uv
RUN uv sync --frozen

# Create logs directory
RUN mkdir -p /logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/1

# Default command (can be overridden in docker-compose)
CMD ["uv", "run", "celery", "-A", "celery_poc.tasks", "worker", "--loglevel=info"]
```

---

## Deployment Strategy

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f worker

# Stop services
docker-compose down

# Full cleanup
docker-compose down -v  # Removes volumes
```

### Production Considerations

1. **Scaling Workers**
```yaml
# docker-compose.yml
worker:
  deploy:
    replicas: 3
```

2. **Redis Persistence**
- Use RDB + AOF for durability
- Configure maxmemory policies
- Regular backups

3. **Monitoring**
- Flower dashboard is included by default
- Consider integrating with Prometheus/Grafana for advanced metrics
- Set up alerting for critical failures

4. **Security**
- Use Redis AUTH
- Network isolation
- Encrypted connections (SSL/TLS)

---

## Testing Approach

### Unit Testing Tasks

```python
# tests/test_tasks.py
from celery import Celery
from celery_poc.tasks import add, multiply

def test_add():
    result = add.apply(args=[2, 2]).get()
    assert result == 4

def test_multiply():
    result = multiply.apply(args=[3, 4]).get()
    assert result == 12
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from celery_poc.tasks import app, add

@pytest.fixture
def celery_config():
    return {
        'broker_url': 'redis://localhost:6379/0',
        'result_backend': 'redis://localhost:6379/1'
    }

def test_task_execution(celery_worker):
    result = add.delay(5, 5)
    assert result.get(timeout=10) == 10
```

---

## Monitoring & Observability

### Key Metrics to Monitor

1. **Task Metrics**
   - Task success/failure rate
   - Task execution time
   - Task retry count
   - Queue depth

2. **Worker Metrics**
   - Worker availability
   - CPU/Memory usage
   - Active tasks
   - Processed tasks per minute

3. **Broker Metrics**
   - Redis memory usage
   - Connection count
   - Message throughput
   - Latency

### Flower Dashboard

Access at: `http://localhost:5555`

Features:
- Real-time task monitoring
- Worker management
- Task history
- Statistics and graphs

---

## Security Considerations

### 1. Serialization Security

```python
# NEVER use pickle in production
task_serializer = 'json'  # Safe
# task_serializer = 'pickle'  # DANGEROUS
```

### 2. Redis Authentication

```python
# celeryconfig.py
broker_url = 'redis://:password@redis:6379/0'
```

### 3. Network Security

- Use Docker networks for isolation
- Implement firewall rules
- Use VPN for multi-datacenter setups

### 4. Task Authorization

```python
# Validate inputs in tasks
@app.task
def secure_task(user_id, data):
    if not validate_user(user_id):
        raise ValueError("Unauthorized")
    # Process data
```

---

## Scalability & Performance

### Horizontal Scaling

```bash
# Add more workers
docker-compose up -d --scale worker=5
```

### Performance Tuning

1. **Prefetch Multiplier**
```python
worker_prefetch_multiplier = 1  # Better distribution
```

2. **Concurrency**
```bash
celery -A tasks worker --concurrency=10
```

3. **Task Priorities**
```python
task.apply_async(args=[...], priority=9)  # 0-9, higher = more priority
```

### Optimization Tips

- Use task routing for specialized workers
- Implement rate limiting for expensive tasks
- Use result expiration to save memory
- Enable task compression for large payloads

---

## Troubleshooting Guide

### Common Issues

1. **Tasks Stay in PENDING**
   - Check worker is running
   - Verify broker connection
   - Ensure result backend is configured

2. **Worker Crashes**
   - Check memory limits
   - Review task code for exceptions
   - Enable `task_acks_late` for reliability

3. **Slow Performance**
   - Reduce prefetch multiplier
   - Increase concurrency
   - Use task routing
   - Profile task code

4. **Redis Out of Memory**
   - Set result expiration
   - Configure maxmemory policy
   - Call `result.forget()` after getting results

### Debugging Commands

```bash
# Check worker status
celery -A celery_poc.tasks inspect active

# Check registered tasks
celery -A celery_poc.tasks inspect registered

# Purge queue
celery -A celery_poc.tasks purge

# Revoke task
celery -A celery_poc.tasks revoke <task-id>

# Check stats
celery -A celery_poc.tasks inspect stats

# Or use uv to run these commands
uv run celery -A celery_poc.tasks inspect active
```

---

## Next Steps

1. **Run the POC**
   - Follow README for setup
   - Execute example tasks
   - Monitor with Flower

2. **Experiment**
   - Modify tasks
   - Try different configurations
   - Test failure scenarios

3. **Production Preparation**
   - Add authentication
   - Implement monitoring
   - Set up alerting
   - Plan scaling strategy

4. **Advanced Features**
   - Periodic tasks (Celery Beat)
   - Custom task classes
   - Workflow patterns
   - Result backends alternatives

---

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Celery](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Status:** Ready for Implementation
