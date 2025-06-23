"""Configuration management for Invest-Pilot MCP Server."""

import os
from typing import Optional
from dataclasses import dataclass
from ..core.exceptions import InvalidConfigurationError

# Try to load .env file automatically
try:
    from dotenv import load_dotenv
    load_dotenv()  # This will load .env file if it exists
except ImportError:
    # dotenv not installed, continue without it
    pass

@dataclass
class AlpacaConfig:
    """Configuration for Alpaca broker."""
    api_key: str
    secret_key: str
    paper: bool = True
    base_url: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key:
            raise InvalidConfigurationError("Alpaca API key is required")
        if not self.secret_key:
            raise InvalidConfigurationError("Alpaca secret key is required")

@dataclass
class ServerConfig:
    """Configuration for the MCP server."""
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise InvalidConfigurationError(f"Invalid log level: {self.log_level}")

def load_alpaca_config() -> AlpacaConfig:
    """
    Load Alpaca configuration from environment variables.
    
    Supports both naming conventions:
    - ALPACA_API_KEY or APCA_API_KEY_ID (standard Alpaca naming)
    - ALPACA_SECRET_KEY or APCA_API_SECRET_KEY (standard Alpaca naming)
    
    Returns:
        AlpacaConfig instance
        
    Raises:
        InvalidConfigurationError: If required environment variables are missing
    """
    # Support multiple environment variable naming conventions
    api_key = (os.getenv("ALPACA_API_KEY") or 
               os.getenv("API_KEY_ID"))
    
    secret_key = (os.getenv("ALPACA_SECRET_KEY") or 
                  os.getenv("API_SECRET_KEY"))
    
    # Check for paper trading setting
    paper_env = os.getenv("ALPACA_PAPER")
    if paper_env is None:
        # No explicit setting, check base URL
        apca_base_url = os.getenv("APCA_API_BASE_URL", "")
        if apca_base_url.endswith("paper-api.alpaca.markets"):
            paper_env = "true"
        else:
            paper_env = "true"  # Default to paper trading for safety
    
    paper = str(paper_env).lower() == "true"
    
    # Base URL with fallback logic
    base_url = (os.getenv("ALPACA_BASE_URL") or 
                os.getenv("APCA_API_BASE_URL"))

    if not api_key:
        raise InvalidConfigurationError(
            "API key is required. Set one of: ALPACA_API_KEY, or API_KEY_ID"
        )
    if not secret_key:
        raise InvalidConfigurationError(
            "Secret key is required. Set one of: ALPACA_SECRET_KEY, or API_SECRET_KEY"
        )
    
    return AlpacaConfig(
        api_key=api_key,
        secret_key=secret_key,
        paper=paper,
        base_url=base_url
    )

def load_server_config() -> ServerConfig:
    """
    Load server configuration from environment variables.
    
    Returns:
        ServerConfig instance
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    return ServerConfig(log_level=log_level) 