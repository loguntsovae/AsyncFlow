from pydantic_settings import BaseSettings
from typing import Dict, List


class Settings(BaseSettings):
    """API Gateway configuration settings."""
    
    # Service host and port
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    
    # Service routes configuration
    SERVICE_ROUTES: Dict[str, Dict[str, str]] = {
        "auth": {
            "host": "http://auth_service:9003",
            "prefix": "auth",
            "public_paths": ["/register", "/token"]
        },
        "orders": {
            "host": "http://order_service:9001",
            "prefix": "orders",
            "public_paths": []
        },
        "billing": {
            "host": "http://billing_service:9002",
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