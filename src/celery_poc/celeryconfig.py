"""
Celery Configuration Module
Following Celery 5.x best practices and recommendations
"""
import os
from kombu import Exchange, Queue

# ============================================================================
# BROKER SETTINGS
# ============================================================================

# Redis as message broker
# Use environment variable or default to Docker hostname
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# Broker connection retry on startup
broker_connection_retry_on_startup = True

# Broker connection retry
broker_connection_retry = True
broker_connection_max_retries = 10

# ============================================================================
# RESULT BACKEND SETTINGS
# ============================================================================

# Redis as result backend
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

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
    'celery_poc.tasks.add': {'queue': 'quick'},
    'celery_poc.tasks.multiply': {'queue': 'quick'},
    'celery_poc.tasks.process_data': {'queue': 'slow'},
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
    'celery_poc.tasks.process_data': {
        'rate_limit': '10/m',  # 10 tasks per minute
        'time_limit': 300,     # Hard time limit (5 minutes)
        'soft_time_limit': 240,  # Soft time limit (4 minutes)
    },
}
