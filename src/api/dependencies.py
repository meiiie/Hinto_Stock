from functools import lru_cache
from src.infrastructure.di_container import DIContainer
from src.application.services.realtime_service import RealtimeService
from src.application.services.paper_trading_service import PaperTradingService
from src.application.services.signal_lifecycle_service import SignalLifecycleService
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.infrastructure.persistence.sqlite_market_data_repository import SQLiteMarketDataRepository
from src.infrastructure.repositories.sqlite_signal_repository import SQLiteSignalRepository


@lru_cache()
def get_container() -> DIContainer:
    """Get singleton instance of DI Container."""
    return DIContainer()


@lru_cache()
def get_order_repository() -> SQLiteOrderRepository:
    """
    Get singleton instance of SQLiteOrderRepository.
    """
    return SQLiteOrderRepository(db_path="data/trading_system.db")


@lru_cache()
def get_signal_repository() -> SQLiteSignalRepository:
    """
    Get singleton instance of SQLiteSignalRepository.
    """
    return SQLiteSignalRepository(db_path="data/trading_system.db")


@lru_cache()
def get_signal_lifecycle_service() -> SignalLifecycleService:
    """
    Get singleton instance of SignalLifecycleService.
    """
    repo = get_signal_repository()
    return SignalLifecycleService(signal_repository=repo)


@lru_cache()
def get_paper_trading_service() -> PaperTradingService:
    """
    Get singleton instance of PaperTradingService.
    """
    repo = get_order_repository()
    market_data_repo = get_market_data_repository()  # SOTA FIX: Inject Market Data Repo
    return PaperTradingService(repository=repo, market_data_repository=market_data_repo)


def get_realtime_service_for_symbol(symbol: str = 'btcusdt') -> RealtimeService:
    """
    Get RealtimeService for a specific symbol.
    
    SOTA Multi-Token: Returns service for the requested symbol.
    """
    container = get_container()
    return container.get_realtime_service(symbol=symbol.lower())


@lru_cache()
def get_realtime_service() -> RealtimeService:
    """
    Get default RealtimeService (BTCUSDT).
    DEPRECATED: Use get_realtime_service_for_symbol for multi-token support.
    """
    container = get_container()
    return container.get_realtime_service(symbol='btcusdt')


@lru_cache()
def get_market_data_repository() -> SQLiteMarketDataRepository:
    """
    SOTA Phase 3: Get MarketDataRepository for hybrid data source.
    SQLite first, Binance fallback.
    """
    container = get_container()
    return container.get_market_data_repository()

