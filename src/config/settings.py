"""
Configuration settings for the Ultimate Gemini MCP server.
"""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_ENHANCEMENT_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_IMAGEN_MODEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TIMEOUT,
    MAX_BATCH_SIZE,
)


class ServerConfig(BaseSettings):
    """Server configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server settings
    transport: str = Field(default="stdio", description="Transport mode: stdio or http")
    host: str = Field(default="localhost", description="Host for HTTP transport")
    port: int = Field(default=8000, description="Port for HTTP transport")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="standard", description="Log format: standard, json, detailed")

    # Output settings
    output_dir: str = Field(
        default=DEFAULT_OUTPUT_DIR, description="Directory for generated images"
    )

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables."""
        return cls()


class APIConfig(BaseSettings):
    """API configuration for Gemini and Imagen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    gemini_api_key: str = Field(
        default="",
        alias="GEMINI_API_KEY",
        description="Gemini API key (also accepts GOOGLE_API_KEY)",
    )

    # Model settings
    default_gemini_model: str = Field(
        default=DEFAULT_GEMINI_MODEL, description="Default Gemini model"
    )
    default_imagen_model: str = Field(
        default=DEFAULT_IMAGEN_MODEL, description="Default Imagen model"
    )
    enhancement_model: str = Field(
        default=DEFAULT_ENHANCEMENT_MODEL, description="Model for prompt enhancement"
    )

    # Feature flags
    enable_prompt_enhancement: bool = Field(
        default=True, description="Enable automatic prompt enhancement"
    )
    enable_batch_processing: bool = Field(default=True, description="Enable batch processing")

    # Request settings
    request_timeout: int = Field(default=DEFAULT_TIMEOUT, description="API request timeout")
    max_batch_size: int = Field(
        default=MAX_BATCH_SIZE, description="Maximum batch size for parallel requests"
    )
    max_retries: int = Field(default=3, description="Maximum number of retries for failed requests")

    # Image settings
    default_aspect_ratio: str = Field(default="1:1", description="Default aspect ratio")
    default_output_format: str = Field(default="png", description="Default output format")

    def __init__(self, **kwargs):
        """Initialize API configuration with fallback for API key."""
        super().__init__(**kwargs)
        # Fallback to GOOGLE_API_KEY if GEMINI_API_KEY not set
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "")

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load API configuration from environment variables."""
        return cls()


class Settings:
    """Combined settings for the server."""

    def __init__(self):
        self.server = ServerConfig.from_env()
        self.api = APIConfig.from_env()

        # Ensure output directory exists
        output_path = Path(self.server.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    @property
    def output_dir(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.server.output_dir)


# Global settings instance (lazy initialization)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
