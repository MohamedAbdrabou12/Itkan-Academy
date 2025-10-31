from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    APP_NAME: str | None = os.getenv("APP_NAME")
    ENV: str | None = os.getenv("ENV")

    # Database
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str | None = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str | None = os.getenv("POSTGRES_PORT")

    # Security
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

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
