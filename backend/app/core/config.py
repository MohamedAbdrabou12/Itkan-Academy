# app/core/config.py
from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "itkan-academy"
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
