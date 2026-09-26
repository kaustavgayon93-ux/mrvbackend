"""
Configuration settings for the Ashtalakshmi MRV platform.
Supports both full Docker deployment and lightweight SQLite local dev.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and environment variables.
    All external service settings have defaults for local development.
    """
    DATABASE_URL: str = "sqlite+aiosqlite:///./mrv_database.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "mrv-data"
    CDSE_USERNAME: str = "demo"
    CDSE_PASSWORD: str = "demo"
    USGS_USERNAME: str = "demo"
    USGS_PASSWORD: str = "demo"
    JWT_SECRET_KEY: str = "ashtalakshmi-mrv-dev-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    TITILER_URL: str = "http://localhost:8090"
    PGTILESERV_URL: str = "http://localhost:7800"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite backend."""
        return "sqlite" in self.DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings. Cached to ensure settings are only loaded once.
    """
    return Settings()
