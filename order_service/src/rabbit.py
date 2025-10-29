import aio_pika
from settings import settings


async def get_connection():
    url = f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_pass}@{settings.rabbitmq_host}:{settings.rabbitmq_port}/"
    return await aio_pika.connect_robust(url)


async def publish_message(event_name: str, message: dict):
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("asyncflow_exchange", aio_pika.ExchangeType.TOPIC)
        await exchange.publish(
            aio_pika.Message(body=str(message).encode()),
            routing_key=event_name,
        )