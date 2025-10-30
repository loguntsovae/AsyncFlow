from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Authentication service configuration settings."""
    
    # Service configuration
    HOST: str = "0.0.0.0"
    PORT: int = 9003
    
    # Database configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5434  # Using a different port to avoid conflicts
    POSTGRES_DB: str = "auth_db"
    
    # JWT configuration
    JWT_SECRET_KEY: str = "your-secret-key"  # Should be overridden in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()