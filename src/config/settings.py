"""Application settings."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Vendor Bid Automation Pipeline"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
