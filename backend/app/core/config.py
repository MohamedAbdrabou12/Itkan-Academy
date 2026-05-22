from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    APP_NAME: str | None = os.getenv("APP_NAME")
    ENV: str | None = os.getenv("ENV")

    # Database
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    # Email Configuration
    MAIL_USERNAME: str | None = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str | None = os.getenv("MAIL_FROM")
    MAIL_PORT: int | None = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str | None = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "True").lower() == "true"

    BROKER_URL: str | None = os.getenv("BROKER_URL")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str | None = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str | None = os.getenv("POSTGRES_PORT")

    # Security
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

    # Frontend URL for password reset links
    FRONTEND_URL: str | None = os.getenv("FRONTEND_URL")

    # CORS – comma-separated origins, e.g. "https://example.com,https://www.example.com"
    ALLOWED_ORIGINS: str | None = os.getenv("ALLOWED_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins list from env or sensible local defaults."""
        if self.ALLOWED_ORIGINS:
            return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

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
