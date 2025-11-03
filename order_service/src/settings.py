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
    """
    Application settings with environment variable support.
    All settings can be overridden using environment variables.
    """
    # Service Settings
    service_name: str = Field("order_service", description="Service name for logs and tracing")
    environment: str = Field("development", description="Deployment environment")

    # RabbitMQ Settings
    rabbitmq_user: str = Field("user", description="RabbitMQ username")
    rabbitmq_pass: SecretStr = Field("pass", description="RabbitMQ password")
    rabbitmq_host: str = Field("rabbitmq", description="RabbitMQ hostname")
    rabbitmq_port: int = Field(5672, ge=1, le=65535, description="RabbitMQ port")
    amqp_exchange: str = Field(
        "asyncflow.exchange",
        description="RabbitMQ exchange name for event publishing"
    )

    # Database Settings
    db_user: str = Field("postgres", description="Database username")
    db_pass: SecretStr = Field("postgres", description="Database password")
    db_host: str = Field("db", description="Database hostname")
    db_port: int = Field(5432, ge=1, le=65535, description="Database port")
    db_name: str = Field("order_service", description="Database name")
    db_pool_size: int = Field(5, ge=1, le=20, description="Database connection pool size")
    db_use_ssl: bool = Field(False, description="Enable SSL for database connection")

    # Security Settings
    cors_origins: Optional[List[str]] = Field(
        None,
        description="Allowed CORS origins. Set via CORS_ORIGINS env var as comma-separated list"
    )
    trusted_hosts: Optional[List[str]] = Field(
        None,
        description="Trusted host patterns. Set via TRUSTED_HOSTS env var as comma-separated list"
    )

    # Logging
    log_level: LogLevel = Field(
        LogLevel.INFO,
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    @validator("cors_origins", "trusted_hosts", pre=True)
    def parse_list_from_str(cls, v):
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @property
    def database_url(self) -> str:
        """Build SQLAlchemy database URL."""
        # Use in-memory SQLite for testing if no host is set
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
