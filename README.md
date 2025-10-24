# Celery PoC
Celery Proof of Concept

## Development Setup

### Prerequisites
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Development Environment
```bash
# Create virtual environment and install dependencies
uv sync --dev

# Activate the virtual environment
source .venv/bin/activate
```

### Development workflow
```bash
# Lint
./dev lint

# Run tests
./dev test

# Start all services (Redis, Worker, Flower)
docker-compose up -d

# Run the client examples
uv run python -m celery_poc.client

# View worker logs
docker-compose logs -f worker

# Access Flower monitoring dashboard
open http://localhost:5555
```
