import json
import logging
from datetime import datetime
from typing import Optional

import aio_pika
from aio_pika import IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.payments import Payment
from src.models.events import OrderCreatedEvent, PaymentProcessedEvent
from src.db.base import async_session


logger = logging.getLogger(__name__)


class OrderConsumer:
    """Consumes order_created events and processes payments."""

    def __init__(self, exchange: aio_pika.abc.AbstractExchange):
        self.exchange = exchange

    async def setup(self) -> None:
        """Setup queue and bind to exchange."""
        channel = self.exchange.channel
        
        # Declare queue
        queue = await channel.declare_queue(
            "billing_orders_queue",
            durable=True,
            auto_delete=False
        )
        
        # Bind to order_created events
        await queue.bind(
            exchange=self.exchange,
            routing_key="order_created"
        )
        
        # Start consuming
        await queue.consume(self.process_message)
        logger.info("Order consumer ready")

    async def process_message(self, message: IncomingMessage) -> None:
        """Process incoming order_created event."""
        async with message.process():
            try:
                # Parse event
                event_data = json.loads(message.body.decode())
                order_event = OrderCreatedEvent(**event_data)
                
                # Process payment
                payment_id = await self.process_payment(order_event)
                
                if payment_id:
                    # Publish result
                    await self.publish_result(
                        order_id=order_event.order_id,
                        user_id=order_event.user_id,
                        payment_id=payment_id,
                        amount=order_event.amount,
                        status="completed"
                    )
                    logger.info(f"Payment processed: order_id={order_event.order_id}")
                else:
                    logger.error(f"Payment failed: order_id={order_event.order_id}")
            
            except Exception as e:
                logger.exception(f"Error processing message: {e}")
                # Requeue if needed (depends on your retry strategy)
                # await message.reject(requeue=True)

    async def process_payment(self, order: OrderCreatedEvent) -> Optional[int]:
        """Process payment for order and return payment_id if successful."""
        async with async_session() as session:
            try:
                # Create payment record
                payment = Payment(
                    order_id=order.order_id,
                    user_id=order.user_id,
                    amount=float(order.amount),
                    status="processing"
                )
                session.add(payment)
                await session.flush()
                
                # TODO: Add actual payment processing logic here
                # For now, simulate success
                payment.status = "completed"
                payment.processed_at = datetime.utcnow()
                
                await session.commit()
                return payment.id
            
            except Exception as e:
                logger.exception(f"Payment processing error: {e}")
                await session.rollback()
                return None

    async def publish_result(
        self,
        order_id: int,
        user_id: int,
        payment_id: int,
        amount: float,
        status: str
    ) -> None:
        """Publish payment_processed event."""
        event = PaymentProcessedEvent(
            order_id=order_id,
            user_id=user_id,
            payment_id=payment_id,
            amount=amount,
            status=status,
            processed_at=datetime.utcnow()
        )
        
        message = aio_pika.Message(
            body=json.dumps(event.model_dump()).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await self.exchange.publish(
            message,
            routing_key="payment_processed"
        )