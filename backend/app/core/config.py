from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # General
    APP_NAME: str = Field(default="Itkan Academy")
    ENV: str = Field(default="development")

    # Database
    POSTGRES_USER: str = Field(default=..., validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default=..., validation_alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default=..., validation_alias="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default=..., validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=..., validation_alias="POSTGRES_PORT")

    # Security
    SECRET_KEY: str | None = None

    # Database URL (auto generated)
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # class Config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
