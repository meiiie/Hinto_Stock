# Backend Engineer Context - Current Codebase State

Version: 1.0 | Updated: 2025-12-22
Based on: Actual codebase audit

---

## CODEBASE OVERVIEW

Location: e:\Sach\DuAn\Hinto_Stock\src\
Architecture: Clean Architecture (4 layers)
Framework: FastAPI 0.1.0
Runtime: Python 3.11+

---

## ARCHITECTURE LAYERS

### 1. API Layer (src/api/)
```
api/
|-- main.py              # FastAPI app with lifespan
|-- event_bus.py         # EventBus for async events (11KB)
|-- websocket_manager.py # WebSocket connections (12KB)
|-- dependencies.py      # DI for FastAPI
+-- routers/
    |-- system.py        # Health check
    |-- market.py        # Market data endpoints (8KB)
    |-- settings.py      # Settings endpoints (3KB)
    +-- trades.py        # Trade endpoints (11KB)
```

Key Features:
- Event-driven architecture with EventBus
- WebSocket for real-time data push
- CORS enabled for Tauri desktop app

### 2. Application Layer (src/application/)
```
application/
|-- services/
|   |-- realtime_service.py          # Main orchestrator (43KB, 1000+ lines)
|   |-- paper_trading_service.py     # Paper trading (21KB)
|   |-- trading_state_machine.py     # State management (11KB)
|   |-- signal_enhancement_service.py # Signal enhancement (9KB)
|   |-- confidence_calculator.py     # Confidence scoring (12KB)
|   |-- entry_price_calculator.py    # Entry calculation (9KB)
|   |-- stop_loss_calculator.py      # SL calculation (21KB)
|   |-- tp_calculator.py             # Take profit levels (18KB)
|   |-- smart_entry_calculator.py    # Smart entry (5KB)
|   |-- hard_filters.py              # ADX/Volume filters (12KB)
|   |-- warmup_manager.py            # Bootstrap warmup (10KB)
|   +-- state_recovery_service.py    # State persistence (14KB)
|-- analysis/                        # Analysis modules
|-- signals/                         # Signal generation
+-- use_cases/                       # Use case handlers
```

### 3. Domain Layer (src/domain/)
```
domain/
|-- entities/
|   |-- candle.py              # OHLCV candle (4KB)
|   |-- trading_signal.py      # Signal entity (2.5KB)
|   |-- enhanced_signal.py     # Enhanced signal (12KB)
|   |-- market_data.py         # Market data (7KB)
|   |-- indicator.py           # Indicator entity (5KB)
|   |-- paper_order.py         # Paper order
|   |-- paper_position.py      # Paper position
|   |-- portfolio.py           # Portfolio state
|   |-- performance_metrics.py # Metrics (4KB)
|   +-- state_models.py        # State machine models (7KB)
|-- interfaces/                # Abstract interfaces
|-- repositories/              # Repository interfaces
|-- services/                  # Domain services
+-- state_machine.py           # State machine base
```

### 4. Infrastructure Layer (src/infrastructure/)
```
infrastructure/
|-- indicators/
|   |-- vwap_calculator.py         # VWAP (5KB) - IMPLEMENTED
|   |-- bollinger_calculator.py    # Bollinger Bands (7KB) - IMPLEMENTED
|   |-- stoch_rsi_calculator.py    # StochRSI (6KB) - IMPLEMENTED
|   |-- adx_calculator.py          # ADX filter (12KB) - IMPLEMENTED
|   |-- atr_calculator.py          # ATR for SL (9KB) - IMPLEMENTED
|   |-- swing_point_detector.py    # Swing highs/lows (10KB) - IMPLEMENTED
|   |-- volume_spike_detector.py   # Volume analysis (8KB) - IMPLEMENTED
|   +-- talib_calculator.py        # TA-Lib wrapper (8KB) - IMPLEMENTED
|-- exchange/                      # Binance integration
|-- websocket/                     # WebSocket client
|-- persistence/                   # Data persistence
|-- aggregation/                   # Candle aggregation
+-- di_container.py               # Dependency injection (22KB)
```

---

## KEY COMPONENTS STATUS

### Signal Generation (Layer 1)
| Component | Status | File | Notes |
|-----------|--------|------|-------|
| VWAP | Done | vwap_calculator.py | Anchored daily VWAP |
| Bollinger Bands | Done | bollinger_calculator.py | SMA(20) +/- 2sigma |
| StochRSI | Done | stoch_rsi_calculator.py | K/D lines |
| Signal Entity | Done | trading_signal.py | With entry/SL/TP |
| Signal Generation | Done | realtime_service.py | In _generate_signals() |

### Risk Management
| Component | Status | File | Notes |
|-----------|--------|------|-------|
| Stop Loss | Done | stop_loss_calculator.py | Swing-based SL |
| Take Profit | Done | tp_calculator.py | Multi-level TP |
| Smart Entry | Done | smart_entry_calculator.py | Optimized entry |
| Confidence | Done | confidence_calculator.py | Score 0-1 |
| Hard Filters | Done | hard_filters.py | ADX, volume |

### State Management
| Component | Status | File | Notes |
|-----------|--------|------|-------|
| State Machine | Done | trading_state_machine.py | BOOTSTRAP/SCANNING/etc |
| Warmup | Done | warmup_manager.py | History loading |
| Recovery | Done | state_recovery_service.py | Persistence |

### Trading
| Component | Status | File | Notes |
|-----------|--------|------|-------|
| Paper Trading | Done | paper_trading_service.py | Full simulation |
| Order Entity | Done | paper_order.py | Order model |
| Position Entity | Done | paper_position.py | Position tracking |

---

## API ENDPOINTS

### Market Data
- GET /market/candles - Historical candles
- GET /market/signals - Current signals
- GET /market/indicators - Indicator values
- WS /ws/market - Real-time WebSocket

### Trades
- GET /trades/history - Trade history
- GET /trades/positions - Open positions
- POST /trades/paper - Paper trade execution

### Settings
- GET /settings - Current settings
- PUT /settings - Update settings

### System
- GET / - Health check
- GET /system/status - System status

---

## ACTIVE ISSUES

| Issue | Severity | Notes |
|-------|----------|-------|
| Sign trade not working | High | Mentioned by user |
| Signal Panel not updating | Medium | Frontend issue |

---

## NEXT PRIORITIES

1. Fix sign trade functionality
2. Verify signal generation flow
3. Ensure WebSocket events reach frontend
4. Add more comprehensive error handling

---

## HOW TO RUN

```bash
# From project root
python run_real_backend.py

# Or directly
uvicorn src.api.main:app --reload --port 8000
```

---

## DEPENDENCIES

Key packages (from requirements.txt):
- fastapi
- uvicorn
- websockets
- ccxt (exchange integration)
- pandas, numpy
- ta-lib (indicators)
- pydantic
