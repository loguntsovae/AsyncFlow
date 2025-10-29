from datetime import datetime
from pydantic import BaseModel, Field, condecimal

# ───────────────────────────────────────────────────────────────
# 🧩 API-модели: запросы и ответы для Order Service
# ───────────────────────────────────────────────────────────────

class OrderBase(BaseModel):
    """Общие поля, которые могут переиспользоваться."""
    user_id: int = Field(..., ge=1, description="ID пользователя")
    amount: condecimal(gt=0, max_digits=10, decimal_places=2) = Field(..., description="Сумма заказа")


class OrderCreate(OrderBase):
    """Модель входных данных при создании заказа."""
    pass


class OrderResponse(BaseModel):
    """Ответ API при создании или запросе заказа."""
    order_id: int = Field(..., description="Уникальный идентификатор заказа")
    created_at: datetime = Field(..., description="Дата и время создания заказа (UTC)")
    message: str = Field(default="OK", description="Описание результата операции")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 101,
                "created_at": "2025-10-29T12:34:56.789Z",
                "message": "Order created and event published",
            }
        }