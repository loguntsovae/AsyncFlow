# 🌀 AsyncFlow

**Event-driven microservice system built with FastAPI + RabbitMQ**

## 🧩 Overview
AsyncFlow is a demo of event-driven architecture:
- **Order Service** creates and publishes events.
- **Billing Service** processes payments asynchronously.
- **Notification Service** reacts to processed payments.

Everything communicates through **RabbitMQ**.

## ⚙️ Stack
- Python 3.12+
- FastAPI
- aio-pika
- RabbitMQ
- Docker Compose
- uv / Poetry


![Tests](https://github.com/<your_username>/<repo_name>/actions/workflows/tests.yml/badge.svg)
