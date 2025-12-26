# Design Document: Production Readiness

## Overview

Spec này implement 3 tính năng critical để chuẩn bị cho Shadow Trading:
1. **State Recovery** - Khôi phục trạng thái khi restart
2. **Real Spread Filter** - Lấy bid/ask thực từ bookTicker
3. **DI Container Refactor** - Inject dependencies đúng cách

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ dependencies.py │  │    main.py      │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           ▼                    ▼                             │
│  ┌─────────────────────────────────────────┐                │
│  │           DIContainer (Updated)          │                │
│  │  - get_trading_state_machine()          │                │
│  │  - get_warmup_manager()                 │                │
│  │  - get_hard_filters()                   │                │
│  │  - get_book_ticker_client()             │                │
│  │  - get_realtime_service()               │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌─────────────────────────────────────────┐                │
│  │         RealtimeService (Updated)        │                │
│  │  - _recover_state() [NEW]               │                │
│  │  - _book_ticker_client [NEW]            │                │
│  └─────────────────────────────────────────┘                │
│                              │                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ StateMachine  │  │ WarmupManager │  │  HardFilters  │   │
│  │   (existing)  │  │   (existing)  │  │  (updated)    │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌─────────────────────────────────────────┐                │
│  │       BookTickerClient [NEW]             │                │
│  │  - subscribe(symbol)                    │                │
│  │  - get_best_bid_ask() -> (bid, ask)     │                │
│  │  - is_data_fresh() -> bool              │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │     SQLiteStateRepository (existing)     │                │
│  │  - get_last_state()                     │                │
│  │  - save_state()                         │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. BookTickerClient (New)

```python
class IBookTickerClient(ABC):
    """Interface for book ticker data provider."""
    
    @abstractmethod
    async def subscribe(self, symbol: str) -> None:
        """Subscribe to bookTicker stream."""
        pass
    
    @abstractmethod
    def get_best_bid_ask(self) -> tuple[float, float]:
        """Get current best bid and ask prices."""
        pass
    
    @abstractmethod
    def is_data_fresh(self, max_age_seconds: float = 5.0) -> bool:
        """Check if data is fresh (not stale)."""
        pass
```

### 2. StateRecoveryService (New)

```python
class StateRecoveryService:
    """Handles state recovery on startup."""
    
    async def recover_state(
        self,
        state_repository: IStateRepository,
        exchange_client: IRestClient,
        state_machine: TradingStateMachine
    ) -> RecoveryResult:
        """
        Recover state from database and verify with exchange.
        
        Returns:
            RecoveryResult with action taken
        """
        pass
```

### 3. HardFilters (Updated)

```python
class HardFilters:
    def __init__(
        self,
        adx_threshold: float = 25.0,
        spread_threshold: float = 0.001,
        book_ticker_client: Optional[IBookTickerClient] = None  # NEW
    ):
        self._book_ticker_client = book_ticker_client
    
    def check_spread_filter_realtime(self) -> FilterResult:
        """Check spread using real bid/ask from bookTicker."""
        if not self._book_ticker_client:
            return FilterResult(passed=False, reason="No bookTicker client")
        
        if not self._book_ticker_client.is_data_fresh():
            return FilterResult(passed=False, reason="Stale spread data")
        
        bid, ask = self._book_ticker_client.get_best_bid_ask()
        return self.check_spread_filter(bid, ask)
```

## Data Models

### RecoveryResult

```python
@dataclass
class RecoveryResult:
    """Result of state recovery attempt."""
    action: str  # "restored", "reset", "no_action"
    previous_state: Optional[SystemState]
    current_state: SystemState
    position_verified: bool
    message: str
```

### BookTickerData

```python
@dataclass
class BookTickerData:
    """Best bid/ask data from Binance."""
    symbol: str
    bid_price: float
    bid_qty: float
    ask_price: float
    ask_qty: float
    timestamp: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: State Recovery Correctness

*For any* persisted state that is IN_POSITION, if the exchange confirms the position exists, the system SHALL restore to IN_POSITION state; if the exchange says no position, the system SHALL transition to SCANNING.

**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: BookTicker Data Freshness

*For any* bookTicker message received, the bid and ask values SHALL be updated and the timestamp SHALL be recorded; subsequent freshness checks SHALL return true if timestamp is within max_age_seconds.

**Validates: Requirements 2.2, 2.4**

### Property 3: Spread Filter Uses Real Data

*For any* spread check when BookTickerClient is configured, the HardFilters SHALL use bid/ask from BookTickerClient instead of estimated values.

**Validates: Requirements 2.3**

## Error Handling

| Error | Handling |
|-------|----------|
| Database unavailable on startup | Log warning, proceed with BOOTSTRAP |
| Exchange API error during recovery | Log error, proceed with BOOTSTRAP |
| BookTicker connection lost | Mark data as stale, block trading |
| Stale bookTicker data | Return FilterResult with passed=False |

## Testing Strategy

### Unit Tests
- StateRecoveryService with mocked repository and exchange
- BookTickerClient message parsing
- HardFilters with injected BookTickerClient

### Property-Based Tests (Hypothesis)
- Property 1: Generate random persisted states and exchange responses
- Property 2: Generate random bookTicker messages and verify freshness
- Property 3: Generate random bid/ask values and verify spread calculation

### Integration Tests
- Full startup flow with recovery
- BookTicker subscription and data flow
