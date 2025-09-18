from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"

    # Database Configuration
    database_url: str = "sqlite:///./llm_agent.db"

    # Security Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # File Upload Configuration
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"

settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)