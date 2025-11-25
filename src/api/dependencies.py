from functools import lru_cache
from src.application.services.realtime_service import RealtimeService
from src.application.services.paper_trading_service import PaperTradingService
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository


@lru_cache()
def get_order_repository() -> SQLiteOrderRepository:
    """
    Get singleton instance of SQLiteOrderRepository.
    """
    return SQLiteOrderRepository(db_path="data/trading_system.db")


@lru_cache()
def get_paper_trading_service() -> PaperTradingService:
    """
    Get singleton instance of PaperTradingService.
    """
    repo = get_order_repository()
    return PaperTradingService(repository=repo)


@lru_cache()
def get_realtime_service() -> RealtimeService:
    """
    Get singleton instance of RealtimeService.
    """
    paper_service = get_paper_trading_service()
    return RealtimeService(
        symbol='btcusdt',
        interval='1m',
        buffer_size=2000,
        paper_service=paper_service
    )
