# AsyncFlow — Event-driven Microservices Demo

A polished, production-minded demonstration of an event-driven microservices architecture implemented with modern Python tooling. AsyncFlow showcases how small, focused services can coordinate asynchronously using message-driven patterns while exposing a unified API gateway.

This repository is prepared for portfolio presentation: it includes design rationale, architecture notes, and clear run / demo instructions so reviewers can quickly understand the goals and verify the implementation.

## What this project demonstrates
- Event-driven communication with RabbitMQ (publisher / consumer pattern)
- Clean service boundaries: Auth, Orders, Billing (each as an independent service)
- API Gateway that aggregates and forwards requests, provides health checks, metrics, rate limiting and auth middleware
- Asynchronous Python with FastAPI, async SQLAlchemy and aio libraries for high throughput
- Docker Compose configuration for reproducible local deployment

## Highlights
- Unified API surface via API Gateway with per-service routing and versioning
- Orders service publishes domain events (order_created) to RabbitMQ
- Billing service consumes events and performs payment processing asynchronously
- Structured JSON logging and Prometheus-compatible metrics (optional)
- Configurable rate limiting and authentication middleware

## Tech stack
- Python 3.12+
- FastAPI
- SQLAlchemy (async)
- aio-pika (RabbitMQ client)
- RabbitMQ (message broker)
- Docker & Docker Compose
- Uvicorn (ASGI server)
- httpx (service-to-service HTTP forwarding)

## Quick start (developer/demo)
These commands assume Docker and Docker Compose are installed. They bring the full system (gateway + services + RabbitMQ) up for local testing.

1) Start the application stack:

```bash
docker compose up --build
```

2) Open the API Gateway docs in your browser (default):

```
http://localhost:9000/api/v1/docs
```

3) Example: create an order (gateway will forward to the Order service):

```bash
curl -X POST http://localhost:9000/api/v1/orders \
	-H "Content-Type: application/json" \
	-d '{"user_id": 1, "amount": 19.99}'
```

4) Check health endpoint:

```
http://localhost:9000/health
```

Try the quick demo script
------------------------
We've included a small convenience script that runs a short demo flow (create order, wait, list orders, show health). It uses `curl` and `jq` to pretty-print JSON.

Prerequisites:
- Docker and Docker Compose
- `jq` (for JSON output) — optional but recommended

Run the demo (starts services if you pass `up`):

```bash
# make script executable once
chmod +x ./scripts/demo.sh

# start services and run demo
./scripts/demo.sh up

# or run just the demo against already-running services
./scripts/demo.sh
```

## API examples
- Create order: POST /api/v1/orders
- List orders: GET /api/v1/orders
- Get order: GET /api/v1/orders/{order_id}
- Gateway docs: /api/v1/docs

These paths reflect the API Gateway routing (see `api_gateway/src/core/config.py` for service routes and versioning).

## How to present this in a portfolio
- Short summary (1–2 sentences) describing the problem solved: "demonstrates event-driven microservices with reliable, async communication via RabbitMQ and a centralized API gateway." 
- Architecture diagram (see `PORTFOLIO.md` for a ready-to-paste ASCII/Markdown diagram)
- Call out important code files: `order_service/src/api/orders.py` (event publishing), `billing_service/src/consumers/order_consumer.py` (event handling), `api_gateway/src/main.py` (forwarding, health, metrics)
- Include a short screencast or GIF showing: API docs -> Create order -> Consumer logs processing payment. (Placeholder instructions in `PORTFOLIO.md`)

## Contributing / extending
If you'd like to extend this demo for an interview or a deeper case study, consider:
- Adding an idempotent consumer pattern for at-least-once delivery guarantees
- Instrumenting distributed tracing (OpenTelemetry)
- Adding automated end-to-end tests that run in CI using Docker Compose + test fixtures

## License
This project is released under the terms of the MIT License. See `LICENSE` for details.

## Contact / Demo notes
If you're presenting this in a portfolio, list a short contact line or link to a short video demo. Replace placeholder assets and badges (CI, coverage) with your own project's links.
