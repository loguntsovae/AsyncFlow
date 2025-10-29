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

## 🚀 Run locally
```bash
cp .env.example .env
make up

RabbitMQ Management UI → http://localhost:15672
Login: user / pass

---

## 🧩 common/shared_schemas.py

(чтобы все сервисы могли использовать одни и те же структуры сообщений)

```python
from pydantic import BaseModel
from datetime import datetime

class OrderCreated(BaseModel):
    event: str = "order_created"
    order_id: int
    user_id: int
    amount: float

class PaymentProcessed(BaseModel):
    event: str = "payment_processed"
    order_id: int
    user_id: int
    status: str
    processed_at: datetime