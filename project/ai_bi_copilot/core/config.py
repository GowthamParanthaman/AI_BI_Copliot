from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Application Settings
    """

    # ==========================================
    # Application
    # ==========================================

    APP_NAME: str = "AI BI Copilot"

    API_V1_PREFIX: str = "/api/v1"

    DEBUG: bool = True

    LOG_LEVEL: str = "INFO"

    # ==========================================
    # Database
    # ==========================================

    DATABASE_TYPE: str = "sqlite"

    DATABASE_NAME: str = "ai_bi.db"

    POSTGRES_HOST: str = "localhost"

    POSTGRES_PORT: int = 5432

    POSTGRES_DB: str = "bi_copilot"

    POSTGRES_USER: str = "postgres"

    POSTGRES_PASSWORD: str = "postgres"

    # ==========================================
    # AI / LLM
    # ==========================================

    OPENAI_API_KEY: SecretStr = SecretStr("")

    OPENAI_MODEL: str = "gpt-4o-mini"

    OPENAI_TEMPERATURE: float = 0.2

    OPENAI_MAX_TOKENS: int = 4000

    # ==========================================
    # Email Configuration
    # ==========================================

    EMAIL_ENABLED: bool = True

    EMAIL_HOST: str = "smtp.gmail.com"

    EMAIL_PORT: int = 587

    EMAIL_USERNAME: str = ""

    EMAIL_PASSWORD: str = ""

    EMAIL_FROM_NAME: str = "AI BI Copilot"

    EMAIL_FROM_ADDRESS: str = ""

    EMAIL_USE_TLS: bool = True

    EMAIL_TIMEOUT: int = 30

    EMAIL_MAX_RETRIES: int = 3

    # ==========================================
    # Environment Configuration
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================
    # Database URL Generator
    # ==========================================

    @property
    def database_url(self) -> str:

        if self.DATABASE_TYPE.lower() == "sqlite":

            return f"sqlite:///./{self.DATABASE_NAME}"

        if self.DATABASE_TYPE.lower() == "postgresql":

            return (
                f"postgresql://"
                f"{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )

        raise ValueError(
            f"Unsupported database type: {self.DATABASE_TYPE}"
        )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()