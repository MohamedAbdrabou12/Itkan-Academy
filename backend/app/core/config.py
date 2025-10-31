from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # General
    APP_NAME: str = Field(default="Itkan Academy")
    ENV: str = Field(default="development")

    # Database
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")

    # Security
    SECRET_KEY: str | None = Field(None, env="SECRET_KEY")

    @property
    def DATABASE_URL(self) -> str:
        """Generate async PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# Ensure secret key is set in production
if settings.ENV != "development" and not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in production environment")
