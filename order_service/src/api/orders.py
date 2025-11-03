from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import aio_pika
import json

from src.db.models.orders import Order
from src.models.order_dto import OrderCreate, OrderResponse
from src.api.dependencies import get_db, get_exchange

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    exchange: aio_pika.abc.AbstractExchange = Depends(get_exchange),
):
    """Создаёт заказ и публикует событие order_created."""
    new_order = Order(user_id=order_data.user_id, amount=order_data.amount)
    db.add(new_order)

    try:
        await db.commit()
        await db.refresh(new_order)
    except Exception:
        await db.rollback()
        raise

    event = {
        "event": "order_created",
        "order_id": new_order.id,
        "user_id": new_order.user_id,
        "amount": new_order.amount,
        "created_at": datetime.utcnow().isoformat(),
    }

    message = aio_pika.Message(body=json.dumps(event).encode())
    await exchange.publish(message, routing_key="order_created")

    return OrderResponse(
        order_id=new_order.id,
        created_at=new_order.created_at,
        message="Order created and event published",
    )


@router.get("")
async def list_orders(db: AsyncSession = Depends(get_db)):
    """Возвращает список заказов (упрощённо)."""
    # Return simplified order list with basic fields
    result = await db.execute(text("SELECT id, user_id, amount, status, created_at FROM orders ORDER BY id DESC"))
    rows = result.fetchall()
    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "amount": float(row.amount),
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single order by id."""
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "user_id": order.user_id,
        "amount": float(order.amount),
        "status": order.status,
        "created_at": order.created_at,
    }