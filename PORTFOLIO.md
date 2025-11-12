## AsyncFlow — Portfolio Presentation

This document is crafted to help you present AsyncFlow as a polished portfolio project. Use the text below in a portfolio page, a case study, or a README section on your personal site.

---

## Elevator pitch

AsyncFlow is a small but realistic demonstration of event-driven microservices built with modern Python async tools. It models an e-commerce flow where orders are created via an API gateway, published as domain events to RabbitMQ, and processed by a Billing service asynchronously. The project emphasizes clear boundaries, resilience patterns, observability, and reproducible local deployment using Docker Compose.

## Architecture (short)

Gateway (FastAPI)
  ├─ forwards HTTP requests to services
  ├─ exposes unified docs, health checks and metrics
  └─ provides auth, rate-limiting and logging middleware

Order Service (FastAPI)
  ├─ HTTP API to create/list orders
  └─ publishes "order_created" events to RabbitMQ

Billing Service
  ├─ consumes "order_created" events
  └─ simulates payment processing and updates order state

RabbitMQ
  └─ message bus for decoupled, asynchronous communication

Optional: Notification Service (can be added later) consumes billing results and sends notifications.

## Architecture diagram (Markdown-friendly)

```
+----------------------+        +-----------------+        +------------------+
|     API Gateway      | <----> |   Order Service |  --->  |   RabbitMQ       |
|  (routing, metrics)  |        | (publishes event)|       | (exchange, queues)|
+----------------------+        +-----------------+        +------------------+
                                         |                         |
                                         v                         v
                                  +-----------------+        +------------------+
                                  | Billing Service | <----  | Notification Svc |
                                  | (consumer)      |        | (optional)       |
                                  +-----------------+        +------------------+
```

## Key files to reference
- `api_gateway/src/main.py` — gateway, forwarding logic, health & metrics
- `api_gateway/src/core/config.py` — routing and service discovery config
- `order_service/src/api/orders.py` — POST /orders and event publishing
- `billing_service/src/consumers/order_consumer.py` — event consumer (payment processing)

## Example user flow (script)

1) Open gateway docs: `http://localhost:9000/api/v1/docs`
2) Create an order via gateway:

```bash
curl -X POST http://localhost:9000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": 19.99}'
```

3) Observe logs in the Billing service container: it should receive an `order_created` event and perform processing.

4) Optionally, query the orders list to see updated status (if billing updates the DB):

```bash
curl http://localhost:9000/api/v1/orders
```

## What to highlight in interviews
- Why event-driven? talk about decoupling, scalability, and failure isolation.
- Trade-offs: eventual consistency and message delivery semantics (at-least-once vs exactly-once).
- Observability: structured logs, request tracing opportunities, Prometheus metrics.
- Extensibility: adding new consumers (notifications) without changing producers.

## Suggested visuals to add
- A short GIF: open API docs -> POST /orders -> show Billing logs processing the event.
- Annotated architecture diagram (PNG or SVG) showing data flow and ports.
- CI badge, test coverage badge, and DockerHub/GitHub Packages link if you publish images.

## Code quality notes (talking points)
- Async-first design using FastAPI and async SQLAlchemy.
- Separation of concerns: each service contains only relevant models and APIs.
- Simple configuration via pydantic settings for easy overrides per environment.

## Next steps / improvements (bonus talking points)
- Add e2e tests that run inside Docker Compose and assert event delivery and processing.
- Add distributed tracing with OpenTelemetry and a trace backend (Jaeger)
- Harden consumers by adding idempotency keys and a dead-letter queue for failed messages.

---

Use this page as the basis for a portfolio item. Replace placeholder screenshots and badges with real assets when available.
