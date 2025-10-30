from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class OrderCreatedEvent(BaseModel):
    """Event received from Order Service when order is created."""
    event: str = "order_created"
    order_id: int
    user_id: int
    amount: Decimal
    created_at: datetime


class PaymentProcessedEvent(BaseModel):
    """Event published when payment is processed (success/failed)."""
    event: str = "payment_processed"
    order_id: int
    user_id: int
    payment_id: int
    amount: Decimal
    status: str
    processed_at: datetime