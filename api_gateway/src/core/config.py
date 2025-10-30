from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List


class Settings(BaseSettings):
    """API Gateway configuration settings."""
    
    # Service host and port
    HOST: str = "0.0.0.0"
    PORT: int = Field(9000, env="API_GATEWAY_PORT")
    
    # API Version
    API_VERSION: str = Field("v1", env="API_VERSION")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    # Request timeouts (seconds)
    DEFAULT_TIMEOUT: float = Field(30.0, env="DEFAULT_TIMEOUT")
    LONG_POLLING_TIMEOUT: float = Field(90.0, env="LONG_POLLING_TIMEOUT")
    
    # Metrics
    ENABLE_METRICS: bool = Field(True, env="ENABLE_METRICS")
    METRICS_PATH: str = Field("/metrics", env="METRICS_PATH")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(True, env="CORS_ALLOW_CREDENTIALS")
    
    # Service routes configuration
    SERVICE_ROUTES: Dict[str, Dict[str, str]] = {
        "auth": {
            "host": f"http://auth_service:{Field(9003, env='AUTH_SERVICE_PORT')}",
            "prefix": "auth",
            "public_paths": ["/register", "/token"]
        },
        "orders": {
            "host": f"http://order_service:{Field(9001, env='ORDER_SERVICE_PORT')}",
            "prefix": "orders",
            "public_paths": []
        },
        "billing": {
            "host": f"http://billing_service:{Field(9002, env='BILLING_SERVICE_PORT')}",
            "prefix": "billing",
            "public_paths": []
        }
    }
    
    # JWT configuration
    JWT_SECRET_KEY: str = "your-secret-key"  # Should match auth service
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()