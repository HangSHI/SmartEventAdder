"""
Configuration settings for SmartEventAdder Gmail Add-on API.

This module handles loading environment variables and configuration
from the parent SmartEventAdder project.
"""

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

# Add parent directory to path to access the existing .env file
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

try:
    from dotenv import load_dotenv
    # Load .env from the main SmartEventAdder project root
    env_path = project_root / '.env'
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not installed, environment variables must be set manually")


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Google Cloud Configuration
        self.google_cloud_project_id: Optional[str] = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.google_cloud_location: str = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

        # API Configuration
        self.api_host: str = os.getenv('API_HOST', '0.0.0.0')
        self.api_port: int = int(os.getenv('API_PORT', '8000'))
        self.debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'

        # CORS Configuration
        self.allowed_origins: list = [
            "https://script.google.com",
            "https://mail.google.com",
            "https://workspace.google.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]

        # Add custom origins from environment
        custom_origins = os.getenv('CORS_ORIGINS', '')
        if custom_origins:
            self.allowed_origins.extend([origin.strip() for origin in custom_origins.split(',')])

        # File paths
        self.project_root = project_root
        self.credentials_path = project_root / 'credentials.json'
        self.token_path = project_root / 'token.json'

        # Logging
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')

        # Validation
        self._validate_settings()

    def _validate_settings(self):
        """Validate critical settings."""
        if not self.google_cloud_project_id:
            print("Warning: GOOGLE_CLOUD_PROJECT_ID not set. Some features may not work.")

        if not self.credentials_path.exists():
            print(f"Warning: credentials.json not found at {self.credentials_path}")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or os.getenv('ENVIRONMENT', '').lower() in ['dev', 'development']

    @property
    def credentials_exist(self) -> bool:
        """Check if Google credentials file exists."""
        return self.credentials_path.exists()

    @property
    def token_exists(self) -> bool:
        """Check if Google token file exists."""
        return self.token_path.exists()

    def get_cors_config(self) -> dict:
        """Get CORS configuration for FastAPI."""
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    def get_uvicorn_config(self) -> dict:
        """Get configuration for uvicorn server."""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "log_level": self.log_level.lower(),
            "reload": self.is_development,
            "access_log": True
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures we only create one instance of Settings
    throughout the application lifecycle.
    """
    return Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development-specific settings."""

    def __init__(self):
        super().__init__()
        self.debug = True
        self.log_level = 'DEBUG'
        # Add localhost origins for development
        self.allowed_origins.extend([
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ])


class ProductionSettings(Settings):
    """Production-specific settings."""

    def __init__(self):
        super().__init__()
        self.debug = False
        self.log_level = 'INFO'
        # Remove localhost origins in production
        self.allowed_origins = [
            origin for origin in self.allowed_origins
            if not origin.startswith('http://localhost') and not origin.startswith('http://127.0.0.1')
        ]


def get_environment_settings() -> Settings:
    """Get settings based on environment."""
    env = os.getenv('ENVIRONMENT', 'development').lower()

    if env in ['prod', 'production']:
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# For backward compatibility
settings = get_settings()