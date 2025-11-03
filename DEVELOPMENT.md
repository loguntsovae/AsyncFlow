# Development Guide

## 🛠️ Development Setup

### Prerequisites
- Python 3.11 or later
- Docker and Docker Compose
- uv (fast Python package installer)

### Initial Setup

1. Install uv:
```bash
pip install uv
```

2. Clone the repository:
```bash
git clone git@github.com:loguntsovae/asyncflow.git
cd asyncflow
```

3. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install dependencies (with dev tools):
```bash
# Install base dependencies
uv pip install -e .
# Install development dependencies
uv pip install -e ".[dev]"
```

5. Copy environment example and adjust:
```bash
cp .env.example .env
# Edit .env with your settings
```

## 🚀 Development Workflow

### Running Services Locally

1. Start all services:
```bash
make up
```

2. Start specific service:
```bash
docker compose up api_gateway
```

3. View logs:
```bash
make logs
# Or for specific service:
docker compose logs -f api_gateway
```

### Quality Checks

Run all checks:
```bash
make qa  # Runs format, lint, typecheck, and test
```

Individual checks:
```bash
make format     # Format code with ruff
make lint       # Check code with ruff
make typecheck  # Run mypy type checking
make test       # Run pytest suite
```

### Testing

Run tests:
```bash
# All tests
pytest

# Specific test file
pytest src/tests/test_orders_api.py

# With coverage
pytest --cov=src
```

### Adding Dependencies

1. Add runtime dependency:
```bash
uv pip install package_name
```

2. Add development dependency:
```bash
uv pip install --group dev package_name
```

3. Update pyproject.toml accordingly:
```toml
[project]
dependencies = [
    "package_name>=1.0.0,<2.0"
]

[dependency-groups]
dev = [
    "dev-package>=1.0.0,<2.0"
]
```

## 📦 Building and Deployment

### Building Docker Images

```bash
# Build all services
docker compose build

# Build specific service
docker compose build api_gateway
```

### Running Tests in Docker

```bash
# Build test image
docker build -t asyncflow-test -f order_service/Dockerfile .

# Run tests
docker run --rm asyncflow-test pytest
```

### Production Deployment

1. Set production configuration:
```bash
cp .env.example .env.prod
# Edit .env.prod with production settings
```

2. Deploy with Docker Compose:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🔍 Monitoring & Debugging

### Metrics

Access service metrics:
- API Gateway: http://localhost:9000/metrics
- Order Service: http://localhost:9001/metrics

### Health Checks

Check service health:
- API Gateway: http://localhost:9000/health
- Order Service: http://localhost:9001/health

### Logging

View structured logs:
```bash
# All services
docker compose logs -f | jq .

# Specific service
docker compose logs -f api_gateway | jq .
```

## 📚 Documentation

- API Documentation: http://localhost:9000/api/v1/docs
- ReDoc Interface: http://localhost:9000/api/v1/redoc

## ⚡ Performance Tips

1. Use `uv` for faster dependency installation
2. Keep Docker images minimal with multi-stage builds
3. Enable response compression for larger payloads
4. Use connection pooling for database and HTTP clients
5. Monitor and optimize based on metrics