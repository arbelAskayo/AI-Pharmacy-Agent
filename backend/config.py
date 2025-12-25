"""
Application configuration using Pydantic Settings.
Loads from environment variables and optional .env file.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # OpenAI Configuration
    openai_api_key: str = ""  # Required for chat, but allow empty for health check
    openai_model: str = "gpt-5"  # Default to gpt-5 as per assignment
    
    # Database Configuration
    database_url: str = "sqlite:///./pharmacy.db"
    
    # Application Configuration
    app_name: str = "Pharmacy Assistant"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    @property
    def openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))


# Global settings instance
settings = Settings()

