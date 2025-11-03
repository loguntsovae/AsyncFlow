from pydantic import Field, validator, SecretStr
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum


class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Billing Service settings with environment variable support."""
    # Service
    service_name: str = Field("billing_service", description="Service name for logs and tracing")
    environment: str = Field("development", description="Deployment environment")

    # RabbitMQ
    rabbitmq_user: str = Field("user", description="RabbitMQ username")
    rabbitmq_pass: SecretStr = Field("pass", description="RabbitMQ password")
    rabbitmq_host: str = Field("rabbitmq", description="RabbitMQ hostname")
    rabbitmq_port: int = Field(5672, ge=1, le=65535, description="RabbitMQ port")
    amqp_exchange: str = Field(
        "asyncflow.exchange",
        description="RabbitMQ exchange name for event publishing"
    )

    # Database
    db_user: str = Field("postgres", description="Database username")
    db_pass: SecretStr = Field("postgres", description="Database password")
    db_host: str = Field("db", description="Database hostname")
    db_port: int = Field(5434, ge=1, le=65535, description="Database port")
    db_name: str = Field("billing_service", description="Database name")
    db_pool_size: int = Field(5, ge=1, le=20, description="Database connection pool size")
    db_use_ssl: bool = Field(False, description="Enable SSL for database connection")

    # Logging
    log_level: LogLevel = Field(
        LogLevel.INFO,
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    @property
    def database_url(self) -> str:
        """Build SQLAlchemy database URL."""
        # Use in-memory SQLite for testing
        if self.environment == "test" or not self.db_host:
            return "sqlite+aiosqlite:///:memory:"
        
        # Build PostgreSQL URL for production/development
        url = f"postgresql+asyncpg://{self.db_user}:{self.db_pass.get_secret_value()}"
        url += f"@{self.db_host}:{self.db_port}/{self.db_name}"
        if self.db_use_ssl:
            url += "?ssl=true"
        return url

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Validate settings on import
settings.model_validate(settings.model_dump())