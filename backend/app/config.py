"""Application configuration using Pydantic Settings"""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode")
    
    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    mongodb_database: str = Field(default="hh_analyzer", description="MongoDB database name")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    
    # HeadHunter API
    hh_client_id: str = Field(default="", description="HeadHunter OAuth client ID")
    hh_client_secret: str = Field(default="", description="HeadHunter OAuth client secret")
    hh_redirect_uri: str = Field(
        default="http://localhost:3000/auth/callback",
        description="HeadHunter OAuth redirect URI"
    )
    
    # Cloudflare Worker (Gemini proxy)
    cloudflare_worker_url: str = Field(
        default="https://proud-water-5293.olegvagin1311.workers.dev",
        description="Cloudflare Worker URL for Gemini API"
    )
    gemini_api_key: str = Field(default="", description="Gemini API key (optional, via worker)")
    
    # Hugging Face Inference API
    huggingface_api_token: str = Field(
        default="",
        description="Hugging Face API token for Inference API (get from https://huggingface.co/settings/tokens)"
    )
    huggingface_model: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2",
        description="Hugging Face model name (mistralai/Mistral-7B-Instruct-v0.2, meta-llama/Llama-2-7b-chat-hf, etc.)"
    )
    
    # Ollama (local AI models) - optional, fallback option
    ollama_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API URL (default: http://localhost:11434)"
    )
    ollama_model: str = Field(
        default="mistral",
        description="Ollama model name (mistral, llama2, etc.)"
    )
    
    # Security
    secret_key: str = Field(
        default="",
        description="Secret key for JWT tokens (required, set via SECRET_KEY env var)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # AI Settings
    max_resumes_for_deep_analysis: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum resumes for deep AI analysis"
    )
    max_resumes_from_search: int = Field(
        default=200,
        ge=1,
        le=500,
        description="Maximum resumes to fetch from HeadHunter"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, ge=1, description="Requests per minute limit")
    rate_limit_per_hour: int = Field(default=1000, ge=1, description="Requests per hour limit")
    
    # Logging
    log_format: str = Field(default="json", description="Log format: json or text")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")
    log_file: str = Field(default="", description="Log file path (empty for console only)")
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate secret key"""
        if not v or v == "":
            # Allow empty in development, but warn
            if info.data.get("environment") == "production":
                raise ValueError("SECRET_KEY is required in production environment. Set it via SECRET_KEY environment variable.")
            # In development, generate a random key if not set
            import secrets
            v = secrets.token_urlsafe(32)
        elif v == "your-secret-key-here-change-in-production":
            raise ValueError("SECRET_KEY must be changed from default value. Set it via SECRET_KEY environment variable.")
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.cors_origins, str):
            if "," in self.cors_origins:
                return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
            return [self.cors_origins.strip()] if self.cors_origins.strip() else ["http://localhost:3000"]
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return ["http://localhost:3000"]
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


# Global settings instance
settings = Settings()
