"""
Configuration module for Binance Data Pipeline.

Handles loading and validation of environment variables and application settings.

Expert Feedback 3 Update:
- Added BookTickerConfig for configurable stale data threshold
- Added SafetyConfig for HALTED state behavior
- Added TRADING_MODE for paper/real switching
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


# Default values
DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS = 2.0
DEFAULT_TRADING_MODE = "PAPER"


@dataclass
class BookTickerConfig:
    """
    BookTicker stream configuration.
    
    Controls how stale data is detected and handled.
    
    Attributes:
        max_age_seconds: Maximum age in seconds before data is considered stale.
                        Default is 2.0 seconds per expert recommendation.
    """
    max_age_seconds: float = DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS
    
    def __post_init__(self):
        """Validate and correct invalid values."""
        if self.max_age_seconds <= 0:
            logging.warning(
                f"Invalid MAX_BOOK_TICKER_AGE_SECONDS: {self.max_age_seconds}. "
                f"Using default: {DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS}"
            )
            self.max_age_seconds = DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS


@dataclass
class SafetyConfig:
    """
    Safety and recovery configuration.
    
    Controls behavior during critical states like HALTED.
    
    Attributes:
        allow_auto_resume_from_halted: If False (default), system stays HALTED
                                       after restart and requires manual intervention.
    """
    allow_auto_resume_from_halted: bool = False


@dataclass
class ExchangeConfig:
    """
    Exchange service configuration.
    
    Controls which exchange implementation to use.
    
    Attributes:
        trading_mode: 'PAPER' for paper trading, 'REAL' for live trading
    """
    trading_mode: str = DEFAULT_TRADING_MODE
    
    def __post_init__(self):
        """Validate trading mode."""
        valid_modes = ('PAPER', 'REAL')
        if self.trading_mode.upper() not in valid_modes:
            logging.warning(
                f"Invalid TRADING_MODE: {self.trading_mode}. "
                f"Using default: {DEFAULT_TRADING_MODE}"
            )
            self.trading_mode = DEFAULT_TRADING_MODE
        else:
            self.trading_mode = self.trading_mode.upper()
    
    @property
    def is_paper_trading(self) -> bool:
        """Check if running in paper trading mode."""
        return self.trading_mode == "PAPER"
    
    @property
    def is_real_trading(self) -> bool:
        """Check if running in real trading mode."""
        return self.trading_mode == "REAL"


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
        
        # Expert Feedback 3: New configuration sections
        self._load_book_ticker_config()
        self._load_safety_config()
        self._load_exchange_config()
    
    def _load_book_ticker_config(self) -> None:
        """Load BookTicker configuration from environment."""
        max_age_str = os.getenv("MAX_BOOK_TICKER_AGE_SECONDS", str(DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS))
        try:
            max_age = float(max_age_str)
        except ValueError:
            logging.warning(
                f"Invalid MAX_BOOK_TICKER_AGE_SECONDS value: {max_age_str}. "
                f"Using default: {DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS}"
            )
            max_age = DEFAULT_MAX_BOOK_TICKER_AGE_SECONDS
        
        self.book_ticker = BookTickerConfig(max_age_seconds=max_age)
    
    def _load_safety_config(self) -> None:
        """Load Safety configuration from environment."""
        allow_resume_str = os.getenv("ALLOW_AUTO_RESUME_FROM_HALTED", "false")
        allow_resume = allow_resume_str.lower() in ("true", "1", "yes")
        
        self.safety = SafetyConfig(allow_auto_resume_from_halted=allow_resume)
    
    def _load_exchange_config(self) -> None:
        """Load Exchange configuration from environment."""
        trading_mode = os.getenv("TRADING_MODE", DEFAULT_TRADING_MODE)
        self.exchange = ExchangeConfig(trading_mode=trading_mode)
        
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
            f"base_url='{self.base_url}', "
            f"trading_mode='{self.exchange.trading_mode}', "
            f"max_book_ticker_age={self.book_ticker.max_age_seconds}s, "
            f"allow_auto_resume_from_halted={self.safety.allow_auto_resume_from_halted}"
            f")"
        )
