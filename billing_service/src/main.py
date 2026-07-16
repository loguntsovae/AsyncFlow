import asyncio
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aio_pika
from src.settings import settings
from src.consumers.order_consumer import OrderConsumer


# Setup logging
logger = logging.getLogger("asyncflow.billing_service")
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@asynccontextmanager
async def get_rabbitmq() -> AsyncIterator[aio_pika.abc.AbstractExchange]:
    """Setup RabbitMQ connection, channel and exchange."""
    # Build connection URL
    amqp_url = (
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_pass.get_secret_value()}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/"
    )
    logger.info(
        "Connecting to RabbitMQ: %s",
        amqp_url.replace(settings.rabbitmq_pass.get_secret_value(), "******")
    )

    connection = None
    channel = None
    exchange = None

    try:
        # Connect and setup exchange
        connection = await aio_pika.connect_robust(amqp_url)
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            name=settings.amqp_exchange,
            type=aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        logger.info("RabbitMQ connected")
        yield exchange

    finally:
        # Cleanup
        try:
            if channel and not channel.is_closed:
                await channel.close()
        except Exception as e:
            logger.warning(f"Channel close warning: {e}")

        try:
            if connection and not connection.is_closed:
                await connection.close()
        except Exception as e:
            logger.warning(f"Connection close warning: {e}")

        logger.info("RabbitMQ connection closed")


def start_health_server(port: int = 9002) -> None:
    """Minimal HTTP /health endpoint in a daemon thread.

    Billing is a queue consumer, but the gateway and k8s probes still need an
    HTTP liveness signal. Stdlib server — no extra dependencies.
    """
    import http.server
    import threading

    class HealthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path == "/health":
                body = b'{"status": "healthy", "service": "billing"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *args):  # silence per-request noise
            pass

    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info("Health endpoint listening on :%d/health", port)


async def main() -> None:
    """Main service entry point."""
    start_health_server(int(os.environ.get("BILLING_SERVICE_PORT", "9002")))

    # Create tables on startup (demo-friendly: compose up needs no migration step).
    from src.db.base import Base, engine
    from src.db.models import payments as _payments_models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema ensured")

    async with get_rabbitmq() as exchange:
        # Setup consumer
        consumer = OrderConsumer(exchange)
        await consumer.setup()

        try:
            # Keep service running
            while True:
                await asyncio.sleep(3600)  # 1 hour
        except asyncio.CancelledError:
            logger.info("Shutdown requested")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped")