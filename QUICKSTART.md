# AsyncFlow - Quick Start

Launch the index page with basic API:

```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Build and start services (minimal setup: frontend + gateway + order_service + rabbitmq)
docker compose up --build frontend api_gateway order_service rabbitmq

# 3. Access the app
# Frontend: http://localhost:3000
# API Gateway health: http://localhost:9000/health
# API v1 health: http://localhost:9000/api/v1/health (used by frontend)
```

## What You'll See

- **React Frontend** on port 3000 with AsyncFlow branding
- **Live health check** showing gateway and services status
- **Feature cards** and tech stack display

## Services Running

1. **Frontend (React + Nginx)** - Port 3000
2. **API Gateway (FastAPI)** - Port 9000
3. **Order Service (FastAPI)** - Port 9001
4. **RabbitMQ** - Ports 5672 (AMQP) & 15672 (Management UI)

## Troubleshooting

If health check fails:
```bash
# Check individual service health
curl http://localhost:9000/health
curl http://localhost:9001/api/health

# View logs
docker compose logs -f api_gateway
docker compose logs -f order_service
```

## Optional: Full Stack

To run all services including auth and billing:
```bash
docker compose up --build
```

Note: Auth service requires Postgres. Add to docker-compose.yml if needed.
