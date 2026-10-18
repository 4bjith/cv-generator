from functools import lru_cache
from typing import List, Optional, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    # Application details
    app_name: str = "AI CV Maker API"
    app_env: str = "development"  # development, test, staging, production
    debug: bool = False

    # Routing prefixes
    api_prefix: str = "/api"
    api_v1_prefix: str = "/api/v1"

    # CORS configuration
    cors_allowed_origins: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Authentication & JWT
    jwt_secret_key: str = "insecure-dev-jwt-secret-key-change-in-production-1234567890"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Database Configuration (PostgreSQL + asyncpg)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_cv_maker"
    test_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cv_generator_test"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # AI & Gemini Provider Settings
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-flash-latest"
    gemini_embedding_model: str = "gemini-embedding-001"
    ai_provider: str = "auto"  # auto, gemini, mock

    # Server binding
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_security_in_production(self) -> "Settings":
        """Enforce strong credentials in production and staging environments."""
        env = self.app_env.lower()
        if env in ("production", "staging"):
            if "insecure-dev" in self.jwt_secret_key or len(self.jwt_secret_key) < 32:
                raise ValueError("Insecure or short JWT_SECRET_KEY is not permitted in production/staging environments.")
            if "postgres:postgres@" in self.database_url:
                raise ValueError("Default database credentials in DATABASE_URL are not permitted in production/staging environments.")

            # AI Provider guardrails for production & staging
            ai_prov = (self.ai_provider or "auto").lower()
            if ai_prov == "mock":
                raise ValueError(
                    f"AI_PROVIDER='mock' is not permitted in {env} environment. "
                    "Production must use real AI providers (e.g. 'gemini')."
                )
            if ai_prov in ("gemini", "auto") and (not self.gemini_api_key or not self.gemini_api_key.strip()):
                raise ValueError(
                    f"GEMINI_API_KEY must be configured in {env} environment when AI_PROVIDER is '{ai_prov}'."
                )
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env.lower() == "test"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
