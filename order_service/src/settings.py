from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # RabbitMQ
    rabbitmq_user: str = "user"
    rabbitmq_pass: str = "pass"
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    amqp_exchange: str = "asyncflow.exchange"

    db_user: str = "postgres"
    db_pass: str = "postgres"
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "order_service"

    # CORS / Trusted hosts / Logs
    cors_origins: Optional[List[str]] = None  # CSV через переменную окружения не забудь парсить при необходимости
    trusted_hosts: Optional[List[str]] = None
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"  # удобно для списков/словарей через ENV

settings = Settings()
