from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = "Manim Video Generator API"
    debug: bool = False
    
    # OpenRouter API
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3.5-sonnet"  # Default model
    
    # Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

