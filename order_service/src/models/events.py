from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class OrderCreatedEvent(BaseModel):
    """Событие, публикуемое в RabbitMQ при создании заказа."""
    event: str = "order_created"
    order_id: int
    user_id: int
    amount: Decimal
    created_at: datetime


class PaymentProcessedEvent(BaseModel):
    """Событие, которое публикует billing_service после успешной оплаты."""
    event: str = "payment_processed"
    order_id: int
    user_id: int
    status: str
    processed_at: datetime