"""
Configuration module for Binance Data Pipeline.

Handles loading and validation of environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """
    Configuration manager for the Binance Data Pipeline.
    
    Loads API credentials from .env file and provides centralized
    access to all configuration parameters.
    
    Attributes:
        api_key (str): Binance API key
        api_secret (str): Binance API secret
        db_path (str): Path to SQLite database file
        base_url (str): Binance API base URL
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration by loading environment variables.
        
        Args:
            env_file (str): Path to .env file (default: ".env")
        """
        # Load environment variables from .env file
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        # Note: Don't fallback to default .env for testing isolation
        
        # Load API credentials
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        
        # Load optional configuration with defaults
        self.db_path = os.getenv("DB_PATH", "crypto_data.db")
        self.base_url = os.getenv("BASE_URL", "https://api.binance.com/api/v3")
        
    def validate(self) -> None:
        """
        Validate that all required configuration is present.
        
        Raises:
            ValueError: If required configuration is missing
        """
        missing_fields = []
        
        if not self.api_key:
            missing_fields.append("BINANCE_API_KEY")
        
        if not self.api_secret:
            missing_fields.append("BINANCE_API_SECRET")
        
        if missing_fields:
            raise ValueError(
                f"Missing required API credentials in .env file: {', '.join(missing_fields)}\n"
                f"Please create a .env file with:\n"
                f"BINANCE_API_KEY=your_api_key_here\n"
                f"BINANCE_API_SECRET=your_api_secret_here"
            )
    
    def __repr__(self) -> str:
        """
        String representation of Config (hides sensitive data).
        
        Returns:
            str: Safe string representation
        """
        return (
            f"Config("
            f"api_key={'***' if self.api_key else 'None'}, "
            f"api_secret={'***' if self.api_secret else 'None'}, "
            f"db_path='{self.db_path}', "
            f"base_url='{self.base_url}'"
            f")"
        )
