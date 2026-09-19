"""Application configuration using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://listingadmin:listingpass123@localhost:5432/listing_automation"
    DATABASE_URL_SYNC: str = "postgresql://listingadmin:listingpass123@localhost:5432/listing_automation"

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- JWT ----
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ---- Server ----
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True

    # ---- File Storage ----
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ---- AI (Phase 2) ----
    OPENAI_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    AI_PROVIDER: str = "mock"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
