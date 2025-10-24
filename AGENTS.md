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
  - Runtime: pydantic, python-dotenv, celery[redis], redis, flower
  - Dev: black, ruff, mypy, pytest, pytest-cov

## Docker Compose

This project uses Docker Compose to run the Celery distributed task processing system with Redis and Flower monitoring.

### Architecture

The Docker Compose setup consists of three services:

```
┌─────────────────────────────────────────────────────────────┐
│  REDIS (redis:6379)                                         │
│  • Message broker (queue storage)                           │
│  • Result backend (task results)                            │
│  • Persistent storage with AOF                              │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  CELERY WORKER (celery-worker)                              │
│  • Fetches tasks from Redis queue                           │
│  • Executes task functions                                  │
│  • Stores results back to Redis                             │
│  • Auto-restart on failure                                  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  FLOWER (localhost:5555)                                    │
│  • Real-time web-based monitoring UI                        │
│  • Task history and statistics                              │
│  • Worker management                                        │
│  • Queue inspection                                         │
└─────────────────────────────────────────────────────────────┘
```

### Common Commands

#### Starting and Stopping

```bash
# Start all services (detached mode)
docker-compose up -d

# Start all services (with logs visible)
docker-compose up

# Stop all services (preserves volumes)
docker-compose down

# Stop all services and remove volumes (clean slate)
docker-compose down -v

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart worker
```

#### Viewing Logs

```bash
# View logs from all services
docker-compose logs

# Follow logs from all services (real-time)
docker-compose logs -f

# View logs from specific service
docker-compose logs worker
docker-compose logs redis
docker-compose logs flower

# Follow logs from worker only
docker-compose logs -f worker

# View last 100 lines from worker
docker-compose logs --tail=100 worker
```

#### Service Management

```bash
# Check status of all services
docker-compose ps

# Check detailed service information
docker-compose ps -a

# Scale workers (run multiple worker containers)
docker-compose up -d --scale worker=3

# Rebuild services after code changes
docker-compose build

# Rebuild and restart services
docker-compose up -d --build

# Pull latest images
docker-compose pull
```

#### Accessing Services

```bash
# Access Flower web UI
open http://localhost:5555
# or
curl http://localhost:5555

# Access Redis CLI
docker-compose exec redis redis-cli

# Check Redis connection
docker-compose exec redis redis-cli ping

# Execute shell in worker container
docker-compose exec worker bash

# Run Python shell in worker container
docker-compose exec worker uv run python
```

#### Debugging and Inspection

```bash
# Inspect active tasks
docker-compose exec worker uv run celery -A celery_poc.tasks inspect active

# Inspect registered tasks
docker-compose exec worker uv run celery -A celery_poc.tasks inspect registered

# Check worker stats
docker-compose exec worker uv run celery -A celery_poc.tasks inspect stats

# Purge all pending tasks from queue
docker-compose exec worker uv run celery -A celery_poc.tasks purge

# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Check Redis keys
docker-compose exec redis redis-cli keys '*'

# Monitor Redis commands in real-time
docker-compose exec redis redis-cli monitor
```

#### Cleanup

```bash
# Stop and remove all containers
docker-compose down

# Remove all containers and volumes (fresh start)
docker-compose down -v

# Remove dangling images
docker image prune -f

# Full cleanup (containers, volumes, images)
docker-compose down -v --rmi all
```

### Accessing Flower Dashboard

Once services are running, access the Flower monitoring dashboard at:

**URL**: http://localhost:5555

**Features**:
- **Tasks**: View all task executions (pending, active, completed, failed)
- **Workers**: Monitor worker status, concurrency, and resource usage
- **Broker**: Inspect queue depth and message rates
- **Monitor**: Real-time task execution graph
- **Configuration**: View Celery configuration

### Workflow

Typical development workflow:

```bash
# 1. Start services
docker-compose up -d

# 2. Check logs to ensure everything started
docker-compose logs -f worker

# 3. Open Flower in browser
open http://localhost:5555

# 4. Run your client code to submit tasks
uv run python -m celery_poc.client

# 5. Monitor tasks in Flower dashboard

# 6. View worker logs for debugging
docker-compose logs -f worker

# 7. When done, stop services
docker-compose down
```

### Troubleshooting

#### Worker won't start
```bash
# Check worker logs
docker-compose logs worker

# Common issues:
# - Celery code has syntax errors
# - Redis not healthy yet (wait a few seconds)
# - Port conflicts (check with: docker-compose ps)
```

#### Tasks stay PENDING
```bash
# 1. Check if worker is running
docker-compose ps

# 2. Check worker logs
docker-compose logs worker

# 3. Verify worker can see tasks
docker-compose exec worker uv run celery -A celery_poc.tasks inspect registered

# 4. Check Redis connection
docker-compose exec redis redis-cli ping
```

#### Flower not accessible
```bash
# Check if Flower is running
docker-compose ps flower

# Check Flower logs
docker-compose logs flower

# Verify port not in use
lsof -i :5555

# Restart Flower
docker-compose restart flower
```

#### Code changes not reflected
```bash
# Rebuild images and restart
docker-compose up -d --build

# Or rebuild specific service
docker-compose build worker
docker-compose up -d worker
```

### Environment Variables

Key environment variables used by the Docker Compose setup (defined in `.env`):

- `CELERY_BROKER_URL`: Redis URL for message broker (default: redis://redis:6379/0)
- `CELERY_RESULT_BACKEND`: Redis URL for result storage (default: redis://redis:6379/1)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `LOG_FORMAT`: Log format (pretty, json)

### Volume Mounts

The Docker Compose setup uses these volume mounts:

- `./src:/app/src`: Source code (allows live code editing)
- `./logs:/logs`: Log files (persistent across container restarts)
- `redis_data:/data`: Redis persistence (preserves queue data)

### Performance Tips

```bash
# Increase worker concurrency (more parallel tasks)
docker-compose up -d --scale worker=3

# Monitor resource usage
docker stats celery-worker celery-flower

# View Redis memory usage
docker-compose exec redis redis-cli info memory | grep used_memory_human
```
