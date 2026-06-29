# AsyncFlow

Event-driven microservices demo built with Python and RabbitMQ.

Three independent services (Auth, Orders, Billing) coordinate asynchronously via message-driven patterns, exposed through a unified API gateway.

## Architecture

```
Client -> API Gateway -> Auth Service
                     |
               Order Service -> RabbitMQ -> Billing Service
```

Each service is independently deployable and communicates only via events — no direct service-to-service HTTP calls except through the gateway.

## Stack

- **Python 3.12 / FastAPI** — all services
- **aio-pika** — async RabbitMQ publisher/consumer
- **SQLAlchemy (async)** — order and billing persistence
- **Docker Compose** — single-command local deployment
- **httpx** — API gateway forwarding

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API gateway: `http://localhost:8000`
RabbitMQ management: `http://localhost:15672` (guest/guest)

## Services

| Service | Port | Responsibility |
|---|---|---|
| api_gateway | 8000 | Auth middleware, routing, rate limiting |
| auth_service | 8001 | JWT issuance and validation |
| order_service | 8002 | Create orders, publish order_created events |
| billing_service | 8003 | Consume events, process payments |

## Docs

See [docs/development.md](docs/development.md) for setup, make commands and deployment guide.

## License

MIT
