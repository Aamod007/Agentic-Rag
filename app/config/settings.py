# Copyright 2024
# Directory: yt-agentic-rag/app/config/settings.py

"""
Application Settings - Environment Variable Management.

Loads and validates all configuration from environment variables:
- Supabase credentials for vector database
- OpenAI/Anthropic API keys for LLM
- Google service account for calendar/email tools
- Application settings (log level, environment, etc.)

Uses Pydantic Settings for automatic .env file loading and validation.
"""

from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Required environment variables:
    - SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
    - OPENAI_API_KEY
    
    Optional environment variables:
    - ANTHROPIC_API_KEY (for Claude support)
    - GOOGLE_SERVICE_ACCOUNT_PATH, GOOGLE_CALENDAR_EMAIL (for tools)
    """
    
    # =========================================================================
    # AI Provider Configuration
    # =========================================================================
    ai_provider: Literal["openai", "anthropic", "groq"] = Field(
        default="openai", 
        env="AI_PROVIDER"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_chat_model: str = Field(
        default="gpt-4o", 
        env="OPENAI_CHAT_MODEL"
    )
    
    # Anthropic Configuration (optional)
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_chat_model: str = Field(
        default="claude-3-5-sonnet-20240620", 
        env="ANTHROPIC_CHAT_MODEL"
    )
    
    # Groq Configuration (optional)
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    groq_chat_model: str = Field(
        default="llama-3.3-70b-versatile", 
        env="GROQ_CHAT_MODEL"
    )
    
    # =========================================================================
    # Cal.com Configuration
    # =========================================================================
    # Secrets come from the environment only — never hardcode keys here.
    cal_api_key: str = Field(default="", env="CAL_API_KEY")
    cal_username: str = Field(default="", env="CAL_USERNAME")
    cal_event_type_slug: str = Field(
        default="agentic", 
        env="CAL_EVENT_TYPE_SLUG"
    )
    
    # =========================================================================
    # Email Configuration (for Agentic Tools)
    # =========================================================================
    email_user: str = Field(
        default="", 
        env="EMAIL_USER"
    )
    email_app_password: str = Field(
        default="", 
        env="EMAIL_APP_PASSWORD"
    )
    
    # =========================================================================
    # Google API Configuration (for Agentic Tools)
    # =========================================================================
    # Path to Google service account JSON file
    google_service_account_path: str = Field(
        default="credentials/service_account.json",
        env="GOOGLE_SERVICE_ACCOUNT_PATH"
    )
    
    # Email address for Google Calendar and Gmail (domain-wide delegation)
    # This is the email that will create calendar events and send emails
    google_calendar_email: str = Field(
        default="",
        env="GOOGLE_CALENDAR_EMAIL"
    )
    
    # Calendar ID to create events on (use 'primary' for main calendar)
    google_calendar_id: str = Field(
        default="primary",
        env="GOOGLE_CALENDAR_ID"
    )
    
    # =========================================================================
    # Application Configuration
    # =========================================================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    # Comma-separated list of allowed CORS origins. Set to your frontend
    # origin(s) in production, e.g. "https://yt-agentic-rag.vercel.app"
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    # =========================================================================
    # RAG Configuration
    # =========================================================================
    default_top_k: int = Field(default=6)
    temperature: float = Field(default=0.1)  # LLM temperature
    
    # =========================================================================
    # Agent Configuration
    # =========================================================================
    # Maximum iterations for the agent loop to prevent infinite loops
    max_agent_iterations: int = Field(default=5)
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    Returns:
        Settings instance with all configuration values
    """
    return settings
