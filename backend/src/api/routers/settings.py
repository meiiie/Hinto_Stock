"""
Settings API Router

Handles trading settings configuration.
Requirements: 6.3

SOTA Phase 26: Token Watchlist for per-token signal enable/disable
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from src.api.dependencies import get_paper_trading_service
from src.application.services.paper_trading_service import PaperTradingService
from src.config import DEFAULT_SYMBOLS

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


class SettingsUpdate(BaseModel):
    """Request model for updating settings"""
    risk_percent: Optional[float] = Field(None, ge=0.1, le=10.0, description="Risk per trade (0.1-10%)")
    rr_ratio: Optional[float] = Field(None, ge=1.0, le=5.0, description="Risk/Reward ratio (1.0-5.0)")
    max_positions: Optional[int] = Field(None, ge=1, le=10, description="Max concurrent positions")
    leverage: Optional[int] = Field(None, ge=1, le=20, description="Leverage (1-20x)")
    auto_execute: Optional[bool] = Field(None, description="Auto-execute signals")


class SettingsResponse(BaseModel):
    """Response model for settings"""
    risk_percent: float
    rr_ratio: float
    max_positions: int
    leverage: int
    auto_execute: bool


# SOTA Phase 26: Token Watchlist Models
class TokenWatchlistItem(BaseModel):
    """Single token in watchlist"""
    symbol: str
    enabled: bool = True
    alias: Optional[str] = None  # Display name e.g., "Bitcoin"


class TokenWatchlistUpdate(BaseModel):
    """Request model for updating token watchlist"""
    tokens: List[TokenWatchlistItem]


class TokenWatchlistResponse(BaseModel):
    """Response model for token watchlist"""
    tokens: List[TokenWatchlistItem]


@router.get("", response_model=SettingsResponse)
async def get_settings(
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get current trading settings.
    
    Returns all configurable trading parameters.
    """
    settings = paper_service.get_settings()
    return SettingsResponse(**settings)


@router.post("", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Update trading settings.
    
    Persists settings to SQLite and applies them to subsequent signals.
    Requirements: 6.3
    """
    # Filter out None values
    update_dict = {k: v for k, v in settings_update.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No settings provided to update")
    
    # Update and return new settings
    updated = paper_service.update_settings(update_dict)
    return SettingsResponse(**updated)


# SOTA Phase 26: Token Watchlist Endpoints

# Token alias mapping for display
TOKEN_ALIASES = {
    "BTCUSDT": "Bitcoin",
    "ETHUSDT": "Ethereum",
    "SOLUSDT": "Solana",
    "BNBUSDT": "BNB",
    "TAOUSDT": "Bittensor",
    "FETUSDT": "Fetch.ai",
    "ONDOUSDT": "Ondo",
}


@router.get("/tokens", response_model=TokenWatchlistResponse)
async def get_token_watchlist(
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get token watchlist with enabled/disabled status.
    
    SOTA Phase 26b: Includes both default and custom tokens
    """
    settings = paper_service.repo.get_all_settings()
    
    # Get enabled tokens
    enabled_tokens_str = settings.get('enabled_tokens', '')
    if enabled_tokens_str:
        enabled_tokens = set(enabled_tokens_str.split(','))
    else:
        enabled_tokens = set(DEFAULT_SYMBOLS)
    
    # Get custom tokens
    custom_tokens_str = settings.get('custom_tokens', '')
    custom_tokens = set(custom_tokens_str.split(',')) if custom_tokens_str else set()
    custom_tokens.discard('')  # Remove empty string
    
    # Build response: Default tokens first, then custom tokens
    tokens = []
    
    # Default tokens (marked as is_default for frontend)
    for symbol in DEFAULT_SYMBOLS:
        tokens.append(TokenWatchlistItem(
            symbol=symbol,
            enabled=symbol in enabled_tokens,
            alias=TOKEN_ALIASES.get(symbol)
        ))
    
    # Custom tokens
    for symbol in sorted(custom_tokens):
        tokens.append(TokenWatchlistItem(
            symbol=symbol,
            enabled=symbol in enabled_tokens,
            alias=TOKEN_ALIASES.get(symbol, symbol.replace('USDT', ''))
        ))
    
    return TokenWatchlistResponse(tokens=tokens)


@router.post("/tokens", response_model=TokenWatchlistResponse)
async def update_token_watchlist(
    watchlist: TokenWatchlistUpdate,
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Update token watchlist - enable/disable signal generation per token.
    
    SOTA Phase 26: Per-token signal enable/disable
    """
    # Extract enabled tokens
    enabled_tokens = [t.symbol for t in watchlist.tokens if t.enabled]
    
    # Store as comma-separated string
    paper_service.repo.set_setting('enabled_tokens', ','.join(enabled_tokens))
    
    # Return updated watchlist
    return await get_token_watchlist(paper_service)


@router.get("/strategy")
async def get_strategy_parameters():
    """
    Get current strategy parameters (read-only).
    
    Returns VWAP, Bollinger Bands, and StochRSI configuration.
    Requirements: 6.4
    """
    return {
        "vwap": {
            "enabled": True,
            "description": "Volume Weighted Average Price"
        },
        "bollinger_bands": {
            "period": 20,
            "std_dev": 2.0,
            "description": "Bollinger Bands (20, 2)"
        },
        "stoch_rsi": {
            "rsi_period": 14,
            "stoch_period": 14,
            "k_period": 3,
            "d_period": 3,
            "description": "Stochastic RSI (3, 3, 14, 14)"
        }
    }


# SOTA Phase 26b: Add/Remove Custom Tokens

class AddTokenRequest(BaseModel):
    """Request to add a new token"""
    symbol: str = Field(..., description="Trading symbol (e.g., XRPUSDT)")
    alias: Optional[str] = Field(None, description="Display name (e.g., Ripple)")


class ValidateTokenResponse(BaseModel):
    """Response for token validation"""
    symbol: str
    valid: bool
    message: str


@router.get("/tokens/validate", response_model=ValidateTokenResponse)
async def validate_token(symbol: str):
    """
    Validate if a token symbol is supported by Binance Futures.
    
    SOTA Phase 26b: Binance API validation
    """
    import httpx
    
    symbol = symbol.upper().strip()
    
    # Format check
    if not symbol.endswith("USDT"):
        return ValidateTokenResponse(
            symbol=symbol,
            valid=False,
            message="Symbol must end with USDT (e.g., BTCUSDT)"
        )
    
    # Binance API validation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://fapi.binance.com/fapi/v1/exchangeInfo",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                valid_symbols = [s["symbol"] for s in data.get("symbols", [])]
                if symbol in valid_symbols:
                    return ValidateTokenResponse(
                        symbol=symbol,
                        valid=True,
                        message="Token exists on Binance Futures"
                    )
                else:
                    return ValidateTokenResponse(
                        symbol=symbol,
                        valid=False,
                        message=f"Token {symbol} not found on Binance Futures"
                    )
    except Exception as e:
        # Fallback to format check only if Binance API fails
        return ValidateTokenResponse(
            symbol=symbol,
            valid=True,  # Allow if format OK but API unreachable
            message=f"Could not validate with Binance API. Format OK."
        )


class SearchTokensResponse(BaseModel):
    """Response for token search"""
    symbols: List[str]
    total: int


@router.get("/tokens/search")
async def search_binance_tokens(q: str = "", limit: int = 20):
    """
    Search Binance Futures symbols for autocomplete.
    
    SOTA Phase 26b: Token search feature
    """
    import httpx
    
    q = q.upper().strip()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://fapi.binance.com/fapi/v1/exchangeInfo",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                all_symbols = [s["symbol"] for s in data.get("symbols", []) 
                              if s["symbol"].endswith("USDT") and s.get("status") == "TRADING"]
                
                # Filter by search query
                if q:
                    matched = [s for s in all_symbols if q in s]
                else:
                    matched = all_symbols
                
                return SearchTokensResponse(
                    symbols=matched[:limit],
                    total=len(matched)
                )
            else:
                # Fallback for non-200 response
                return SearchTokensResponse(symbols=[], total=0)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Token search error: {e}")
        return SearchTokensResponse(symbols=[], total=0)


@router.post("/tokens/add", response_model=TokenWatchlistResponse)
async def add_token(
    request: AddTokenRequest,
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Add a new token to the watchlist.
    
    SOTA Phase 26b: Dynamic token management
    """
    symbol = request.symbol.upper().strip()
    
    # Validate format
    if not symbol.endswith("USDT"):
        raise HTTPException(status_code=400, detail="Symbol must end with USDT")
    
    # Get current custom tokens
    settings = paper_service.repo.get_all_settings()
    custom_tokens_str = settings.get('custom_tokens', '')
    custom_tokens = set(custom_tokens_str.split(',')) if custom_tokens_str else set()
    
    # Check if already exists
    if symbol in DEFAULT_SYMBOLS or symbol in custom_tokens:
        raise HTTPException(status_code=400, detail=f"Token {symbol} already exists")
    
    # Add to custom tokens
    custom_tokens.add(symbol)
    paper_service.repo.set_setting('custom_tokens', ','.join(custom_tokens))
    
    # Also enable it by default
    enabled_tokens_str = settings.get('enabled_tokens', '')
    enabled_tokens = set(enabled_tokens_str.split(',')) if enabled_tokens_str else set(DEFAULT_SYMBOLS)
    enabled_tokens.add(symbol)
    paper_service.repo.set_setting('enabled_tokens', ','.join(enabled_tokens))
    
    # Update TOKEN_ALIASES if alias provided
    if request.alias:
        TOKEN_ALIASES[symbol] = request.alias
    
    return await get_token_watchlist(paper_service)


@router.delete("/tokens/{symbol}", response_model=TokenWatchlistResponse)
async def remove_token(
    symbol: str,
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Remove a custom token from the watchlist.
    
    SOTA Phase 26b: Can only remove custom tokens, not default ones.
    """
    symbol = symbol.upper().strip()
    
    # Cannot remove default tokens
    if symbol in DEFAULT_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"Cannot remove default token {symbol}")
    
    # Get current custom tokens
    settings = paper_service.repo.get_all_settings()
    custom_tokens_str = settings.get('custom_tokens', '')
    custom_tokens = set(custom_tokens_str.split(',')) if custom_tokens_str else set()
    
    # Check if exists
    if symbol not in custom_tokens:
        raise HTTPException(status_code=404, detail=f"Token {symbol} not found in custom tokens")
    
    # Remove from custom tokens
    custom_tokens.discard(symbol)
    paper_service.repo.set_setting('custom_tokens', ','.join(custom_tokens))
    
    # Also remove from enabled tokens
    enabled_tokens_str = settings.get('enabled_tokens', '')
    if enabled_tokens_str:
        enabled_tokens = set(enabled_tokens_str.split(','))
        enabled_tokens.discard(symbol)
        paper_service.repo.set_setting('enabled_tokens', ','.join(enabled_tokens))
    
    return await get_token_watchlist(paper_service)
