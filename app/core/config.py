# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
