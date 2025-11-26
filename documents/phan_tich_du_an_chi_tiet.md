# 📊 PHÂN TÍCH CHI TIẾT DỰ ÁN HINTO TRADER PRO

**Ngày phân tích:** 26/11/2025  
**Mục đích:** Làm sạch dự án - Xác định các thành phần cần giữ, loại bỏ, và tái cấu trúc

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Mục tiêu
- **Ứng dụng Desktop Trading** cho cryptocurrency (BTC/USDT)
- **Chiến lược:** Trend Pullback (VWAP + Bollinger Bands + StochRSI) trên khung 15m/1h
- **Paper Trading:** 7 ngày mô phỏng trước khi trade thật
- **Hiệu năng:** 60fps, giao diện chuyên nghiệp như Binance Desktop

### 1.2 Kiến trúc
```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP APP (Tauri)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              React Frontend (TypeScript)             │    │
│  │  - CandleChart (TradingView Lightweight Charts)     │    │
│  │  - Portfolio, TradeHistory, Settings                │    │
│  │  - Client-Side Candle Aggregation (1m → 15m/1h)    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                    HTTP REST + WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (:8000)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  API Layer: /system, /market, /trades, /settings    │    │
│  │  WebSocket: /ws/stream/{symbol}                     │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Application Layer:                                  │    │
│  │  - RealtimeService (Singleton - Data Orchestrator)  │    │
│  │  - PaperTradingService (Trade Execution)            │    │
│  │  - SignalGenerator (Strategy Logic)                 │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Infrastructure Layer:                               │    │
│  │  - BinanceWebSocketClient (Market Data)             │    │
│  │  - SQLite Repository (Persistence)                  │    │
│  │  - Indicator Calculators (VWAP, BB, StochRSI, ATR)  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                         Binance API
```

---

## 2. CẤU TRÚC THƯ MỤC HIỆN TẠI

### 2.1 Thư mục GỐC
```
Hinto_Stock/
├── .kiro/specs/              # ✅ GIỮ - Spec documents
├── .streamlit/               # ⚠️ XEM XÉT - Cũ (Streamlit dashboard)
├── backups/                  # ✅ GIỮ - Database backups
├── ChuyenGia/phanhoi/        # ✅ GIỮ - Expert feedback docs
├── data/                     # ✅ GIỮ - Trading data
├── documents/                # ✅ GIỮ - Project documentation
├── frontend/                 # ✅ GIỮ - React/Tauri frontend
├── reports/                  # ⚠️ TRỐNG - Có thể xóa
├── scripts/                  # ⚠️ XEM XÉT - Nhiều script cũ
├── src/                      # ✅ GIỮ - Python backend
├── tests/                    # ✅ GIỮ - Test files
├── .env                      # ✅ GIỮ - Environment config
├── crypto_data.db            # ⚠️ XEM XÉT - DB cũ?
├── nonexistent.db            # ❌ XÓA - File rác
├── pytest.ini                # ✅ GIỮ
├── requirements.txt          # ✅ GIỮ
├── run_real_backend.py       # ⚠️ XEM XÉT
├── test_backend.py           # ⚠️ XEM XÉT - Có thể move vào tests/
├── test_integration.py       # ⚠️ XEM XÉT - Có thể move vào tests/
└── launch_dashboard.bat      # ⚠️ XEM XÉT - Cũ (Streamlit)
```

---

## 3. PHÂN TÍCH BACKEND (src/)

### 3.1 Cấu trúc hiện tại
```
src/
├── api/                      # ✅ CORE - FastAPI endpoints
│   ├── main.py               # Entry point
│   ├── websocket_manager.py  # WebSocket Pub/Sub
│   ├── dependencies.py       # DI container
│   └── routers/
│       ├── system.py         # /system/status
│       ├── market.py         # /ws/*, /market/*
│       ├── trades.py         # /trades/*
│       └── settings.py       # /settings
│
├── application/              # ✅ CORE - Business logic
│   ├── services/
│   │   ├── realtime_service.py       # ⭐ QUAN TRỌNG - Data orchestrator
│   │   ├── paper_trading_service.py  # ⭐ QUAN TRỌNG - Trade engine
│   │   ├── confidence_calculator.py
│   │   ├── entry_price_calculator.py
│   │   ├── smart_entry_calculator.py
│   │   ├── stop_loss_calculator.py
│   │   ├── tp_calculator.py
│   │   ├── dashboard_service.py      # ⚠️ XEM XÉT - Cũ?
│   │   ├── pipeline_service.py       # ⚠️ XEM XÉT - Cũ?
│   │   ├── realtime_service_threaded.py  # ⚠️ DUPLICATE?
│   │   └── signal_enhancement_service.py # ⚠️ XEM XÉT
│   ├── analysis/
│   │   ├── ema_crossover.py
│   │   ├── rsi_monitor.py
│   │   ├── trend_filter.py
│   │   └── volume_analyzer.py
│   ├── signals/
│   │   └── signal_generator.py       # ⭐ QUAN TRỌNG - Strategy
│   ├── use_cases/                    # ⚠️ XEM XÉT - Có dùng không?
│   │   ├── calculate_indicators.py
│   │   ├── export_data.py
│   │   ├── fetch_market_data.py
│   │   └── validate_data.py
│   └── dto/                          # ⚠️ XEM XÉT
│
├── domain/                   # ✅ CORE - Domain entities
│   ├── entities/
│   │   ├── candle.py                 # ⭐ QUAN TRỌNG
│   │   ├── trading_signal.py         # ⭐ QUAN TRỌNG
│   │   ├── paper_position.py         # ⭐ QUAN TRỌNG
│   │   ├── portfolio.py              # ⭐ QUAN TRỌNG
│   │   ├── performance_metrics.py    # ⭐ QUAN TRỌNG
│   │   ├── enhanced_signal.py        # ⚠️ XEM XÉT
│   │   ├── indicator.py              # ⚠️ XEM XÉT - Cũ?
│   │   └── market_data.py            # ⚠️ XEM XÉT - Cũ?
│   ├── repositories/
│   │   ├── i_order_repository.py     # Interface
│   │   ├── market_data_repository.py # ⚠️ XEM XÉT
│   │   └── indicator_repository.py   # ⚠️ XEM XÉT
│   └── services/                     # ⚠️ TRỐNG?
│
├── infrastructure/           # ✅ CORE - External integrations
│   ├── api/
│   │   ├── binance_client.py         # ⚠️ DUPLICATE với binance_rest_client?
│   │   └── binance_rest_client.py    # ⭐ QUAN TRỌNG
│   ├── websocket/
│   │   ├── binance_websocket_client.py  # ⭐ QUAN TRỌNG
│   │   └── message_parser.py
│   ├── aggregation/
│   │   └── data_aggregator.py        # ⭐ QUAN TRỌNG
│   ├── indicators/
│   │   ├── talib_calculator.py       # ⭐ QUAN TRỌNG
│   │   ├── vwap_calculator.py        # ⭐ QUAN TRỌNG
│   │   ├── bollinger_calculator.py   # ⭐ QUAN TRỌNG
│   │   ├── stoch_rsi_calculator.py   # ⭐ QUAN TRỌNG
│   │   ├── atr_calculator.py         # ⭐ QUAN TRỌNG
│   │   ├── adx_calculator.py         # ⭐ QUAN TRỌNG
│   │   ├── volume_spike_detector.py
│   │   └── swing_point_detector.py
│   ├── persistence/
│   │   └── sqlite_order_repository.py  # ⭐ QUAN TRỌNG
│   ├── database/
│   │   └── sqlite_repository.py      # ⚠️ DUPLICATE?
│   ├── config/                       # ⚠️ XEM XÉT
│   └── di_container.py
│
├── presentation/             # ⚠️ XEM XÉT - Streamlit cũ?
│   ├── dashboard/
│   │   ├── app.py                    # ⚠️ Streamlit app
│   │   ├── pages/
│   │   │   ├── home.py
│   │   │   ├── charts.py
│   │   │   ├── monitoring.py
│   │   │   └── settings.py
│   │   ├── components/
│   │   │   ├── price_ticker.py
│   │   │   ├── multi_chart.py
│   │   │   ├── signals_panel.py
│   │   │   ├── volume_indicator.py
│   │   │   ├── rsi_gauge.py
│   │   │   └── connection_status.py
│   │   ├── utils/
│   │   │   ├── state_manager.py
│   │   │   ├── cache_manager.py
│   │   │   └── formatters.py
│   │   └── config/
│   │       └── theme_config.py
│   └── cli/                          # ⚠️ XEM XÉT
│
├── utils/
│   └── logging_config.py
│
└── [ROOT FILES - CŨ]
    ├── binance_client.py             # ❌ DUPLICATE - Xóa
    ├── config.py                     # ⚠️ XEM XÉT
    ├── database.py                   # ⚠️ XEM XÉT - Cũ?
    ├── indicators.py                 # ❌ DUPLICATE - Xóa
    ├── pipeline.py                   # ⚠️ XEM XÉT - Cũ?
    └── validator.py                  # ⚠️ XEM XÉT
```

### 3.2 Các file DUPLICATE cần xử lý
| File cũ | File mới | Hành động |
|---------|----------|-----------|
| `src/binance_client.py` | `src/infrastructure/api/binance_rest_client.py` | Xóa file cũ |
| `src/indicators.py` | `src/infrastructure/indicators/*` | Xóa file cũ |
| `src/database.py` | `src/infrastructure/persistence/sqlite_order_repository.py` | Xóa file cũ |
| `src/infrastructure/api/binance_client.py` | `src/infrastructure/api/binance_rest_client.py` | Merge hoặc xóa |
| `src/infrastructure/database/sqlite_repository.py` | `src/infrastructure/persistence/sqlite_order_repository.py` | Merge hoặc xóa |

---

## 4. PHÂN TÍCH FRONTEND (frontend/)

### 4.1 Cấu trúc hiện tại
```
frontend/
├── src/
│   ├── App.tsx               # ⭐ QUAN TRỌNG - Main layout
│   ├── main.tsx              # Entry point
│   ├── index.css             # Global styles
│   ├── App.css               # ⚠️ XEM XÉT - Có dùng không?
│   │
│   ├── components/
│   │   ├── CandleChart.tsx           # ⭐ QUAN TRỌNG - TradingView chart
│   │   ├── Portfolio.tsx             # ⭐ QUAN TRỌNG
│   │   ├── TradeHistory.tsx          # ⭐ QUAN TRỌNG
│   │   ├── PerformanceDashboard.tsx  # ⭐ QUAN TRỌNG
│   │   ├── Settings.tsx              # ⭐ QUAN TRỌNG
│   │   ├── ConnectionStatus.tsx      # ⭐ QUAN TRỌNG
│   │   ├── PriceTicker.tsx           # ⚠️ XEM XÉT - Có dùng không?
│   │   ├── StrategyMonitor.tsx       # ✅ GIỮ
│   │   └── SignalLogItem.tsx         # ✅ GIỮ
│   │
│   ├── hooks/
│   │   └── useMarketData.ts          # ⭐ QUAN TRỌNG - WebSocket hook
│   │
│   ├── utils/
│   │   ├── candleAggregator.ts       # ⭐ QUAN TRỌNG - Client-side aggregation
│   │   └── candleAggregator.test.ts  # ✅ GIỮ - Property test
│   │
│   ├── styles/
│   │   └── theme.ts                  # ⭐ QUAN TRỌNG - Design tokens
│   │
│   └── assets/                       # ⚠️ XEM XÉT
│
├── src-tauri/                # ✅ GIỮ - Tauri config
│   ├── src/
│   ├── Cargo.toml
│   └── tauri.conf.json
│
├── thamkhao/                 # ⚠️ XEM XÉT - Reference docs
│
├── package.json              # ✅ GIỮ
├── vite.config.ts            # ✅ GIỮ
├── vitest.config.ts          # ✅ GIỮ
├── tsconfig.json             # ✅ GIỮ
└── postcss.config.js         # ✅ GIỮ
```

### 4.2 Components Analysis

| Component | Trạng thái | Chức năng | Ghi chú |
|-----------|------------|-----------|---------|
| `App.tsx` | ✅ ACTIVE | Main layout, routing, header | Binance-style layout |
| `CandleChart.tsx` | ✅ ACTIVE | TradingView chart với VWAP, BB | 977 lines - cần refactor? |
| `Portfolio.tsx` | ✅ ACTIVE | Balance, positions, PnL | Inline styles (Tailwind v4 fix) |
| `TradeHistory.tsx` | ✅ ACTIVE | Paginated trade history | |
| `PerformanceDashboard.tsx` | ✅ ACTIVE | Win rate, profit factor, drawdown | |
| `Settings.tsx` | ✅ ACTIVE | Risk %, R:R, debug buttons | |
| `ConnectionStatus.tsx` | ✅ ACTIVE | WebSocket status indicator | |
| `StrategyMonitor.tsx` | ✅ ACTIVE | Trend bias, ADX, StochRSI | |
| `SignalLogItem.tsx` | ✅ ACTIVE | Live feed log item | |
| `PriceTicker.tsx` | ⚠️ CHECK | Price display | Có thể không dùng |

---

## 5. PHÂN TÍCH SCRIPTS (scripts/)

### 5.1 Cấu trúc hiện tại
```
scripts/
├── backtesting/              # ⚠️ XEM XÉT - Có dùng không?
│   ├── data_loader.py
│   ├── trade_simulator.py
│   ├── performance_analyzer.py
│   ├── report_generator.py
│   ├── run_backtest.py
│   ├── test_framework.py
│   └── debug_*.py            # ❌ XÓA - Debug files
│
├── debug/                    # ❌ XÓA - Debug scripts
│   ├── debug_entry_calculator.py
│   ├── debug_rsi.py
│   ├── debug_service.py
│   └── debug_signal_alerts.py
│
├── production/               # ⚠️ XEM XÉT
│   ├── backup_db.py
│   ├── monitor_indicators.py
│   ├── monitor_pipeline.py
│   └── run_pipeline_v2.py
│
├── tests/                    # ⚠️ XEM XÉT - Move to tests/?
│   ├── integration/
│   └── unit/
│
├── utilities/                # ⚠️ XEM XÉT
│   ├── check_status.py
│   ├── generate_expert_report.py
│   ├── validate_data.py
│   ├── verify_ema25.py
│   └── verify_indicators.py
│
├── analyze_losers.py         # ⚠️ XEM XÉT
├── fetch_data.py             # ⚠️ XEM XÉT
├── initialize_db.py          # ⚠️ XEM XÉT
├── run_live_demo.py          # ⚠️ XEM XÉT
├── run_simulation.py         # ⚠️ XEM XÉT
└── test_binance.py           # ⚠️ XEM XÉT
```

---

## 6. PHÂN TÍCH TESTS (tests/)

### 6.1 Cấu trúc hiện tại
```
tests/
├── property/                 # ✅ GIỮ - Property-based tests
│   ├── test_api_properties.py
│   ├── test_historical_api_properties.py
│   ├── test_pagination_properties.py
│   ├── test_performance_metrics_properties.py
│   ├── test_persistence_properties.py
│   ├── test_pnl_calculation_properties.py
│   ├── test_settings_properties.py
│   └── test_stability_properties.py
│
├── unit/                     # ✅ GIỮ
│   └── test_websocket_manager.py
│
├── [ROOT TEST FILES]         # ⚠️ XEM XÉT - Tổ chức lại
│   ├── test_adx_calculator.py
│   ├── test_aggregator.py
│   ├── test_atr_calculator.py
│   ├── test_binance_client.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_domain_entities.py
│   ├── test_indicators.py
│   ├── test_rsi_monitor.py
│   ├── test_signal_generator_integration.py
│   ├── test_signal_generator_strict.py
│   ├── test_signal_integration.py
│   ├── test_stop_loss_atr.py
│   ├── test_tp_atr.py
│   ├── test_trend_filter.py
│   ├── test_validator.py
│   └── test_volume_analyzer.py
```

### 6.2 Test Coverage
- **Property Tests:** 8 files (55 tests) - Validates spec requirements
- **Unit Tests:** 17 files - Component-level testing
- **Integration Tests:** 2 files - End-to-end flows

---

## 7. ĐỀ XUẤT LÀM SẠCH

### 7.1 Files/Folders CẦN XÓA
```
❌ XÓA NGAY:
- nonexistent.db
- src/binance_client.py (duplicate)
- src/indicators.py (duplicate)
- scripts/debug/ (toàn bộ folder)
- scripts/backtesting/debug_*.py
- .hypothesis/ (có thể regenerate)
- __pycache__/ (tất cả)
```

### 7.2 Files/Folders CẦN XEM XÉT
```
⚠️ XEM XÉT:
- src/presentation/dashboard/ (Streamlit cũ - có cần không?)
- src/database.py (có dùng không?)
- src/pipeline.py (có dùng không?)
- src/config.py (có dùng không?)
- src/validator.py (có dùng không?)
- src/application/use_cases/ (có dùng không?)
- src/application/services/dashboard_service.py
- src/application/services/pipeline_service.py
- src/application/services/realtime_service_threaded.py
- scripts/ (nhiều script có thể không cần)
- .streamlit/ (Streamlit config cũ)
- launch_dashboard.bat (Streamlit launcher)
- run_backtest.bat
- crypto_data.db (DB cũ?)
```

### 7.3 Files CẦN MERGE/REFACTOR
```
🔄 MERGE:
- src/infrastructure/api/binance_client.py + binance_rest_client.py
- src/infrastructure/database/sqlite_repository.py + persistence/sqlite_order_repository.py
```

### 7.4 Cấu trúc ĐỀ XUẤT sau khi làm sạch
```
Hinto_Stock/
├── .kiro/specs/              # Spec documents
├── data/                     # Trading data
├── documents/                # Documentation
├── frontend/                 # React/Tauri frontend
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── utils/
│       └── styles/
├── src/                      # Python backend
│   ├── api/                  # FastAPI endpoints
│   ├── application/          # Business logic
│   │   ├── services/
│   │   ├── analysis/
│   │   └── signals/
│   ├── domain/               # Domain entities
│   │   ├── entities/
│   │   └── repositories/
│   ├── infrastructure/       # External integrations
│   │   ├── api/
│   │   ├── websocket/
│   │   ├── indicators/
│   │   └── persistence/
│   └── utils/
├── tests/                    # All tests
│   ├── property/
│   ├── unit/
│   └── integration/
├── scripts/                  # Utility scripts (minimal)
│   └── production/
├── .env
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 8. TỔNG KẾT

### 8.1 Thống kê
| Loại | Số lượng | Ghi chú |
|------|----------|---------|
| Backend Python files | ~60 | Nhiều duplicate |
| Frontend TSX files | ~15 | Tương đối clean |
| Test files | ~25 | Tốt |
| Script files | ~30 | Nhiều không cần |
| Duplicate files | ~10 | Cần xóa |

### 8.2 Ưu tiên làm sạch
1. **Cao:** Xóa files duplicate và debug
2. **Trung bình:** Xóa/archive Streamlit code
3. **Thấp:** Tổ chức lại tests và scripts

### 8.3 Rủi ro
- Xóa nhầm file đang dùng → **Backup trước khi xóa**
- Import paths bị hỏng → **Chạy tests sau mỗi thay đổi**
- Mất code cũ cần tham khảo → **Move vào archive/ thay vì xóa**


---

## 9. PHÂN TÍCH CHI TIẾT CÁC SERVICES

### 9.1 RealtimeService (src/application/services/realtime_service.py)
**Vai trò:** Singleton orchestrator - Điều phối toàn bộ data flow

**Dependencies:**
```python
- BinanceWebSocketClient      # Nhận data từ Binance
- BinanceRestClient           # Fetch historical data
- DataAggregator              # Aggregate 1m → 15m/1h
- VolumeAnalyzer, RSIMonitor  # Analysis (có thể không dùng)
- SignalGenerator             # Generate trading signals
- TALibCalculator             # Technical indicators
- VWAPCalculator              # VWAP calculation
- BollingerCalculator         # Bollinger Bands
- StochRSICalculator          # Stochastic RSI
- EntryPriceCalculator        # Entry price logic
- TPCalculator                # Take profit levels
- StopLossCalculator          # Stop loss calculation
- ConfidenceCalculator        # Signal confidence
- SmartEntryCalculator        # Smart entry logic
- VolumeSpikeDetector         # Volume spike detection
- ADXCalculator               # ADX trend strength
- ATRCalculator               # ATR volatility
- PaperTradingService         # Paper trading execution
```

**Data Flow:**
```
Binance WebSocket (1m candles)
        │
        ▼
┌───────────────────┐
│  RealtimeService  │
│  ┌─────────────┐  │
│  │ _candles_1m │  │ ← Buffer (deque, maxlen=2000)
│  │ _candles_15m│  │
│  │ _candles_1h │  │
│  └─────────────┘  │
│         │         │
│         ▼         │
│  ┌─────────────┐  │
│  │ Aggregator  │  │ → Aggregate 1m → 15m/1h
│  └─────────────┘  │
│         │         │
│         ▼         │
│  ┌─────────────┐  │
│  │SignalGen    │  │ → Generate BUY/SELL signals
│  └─────────────┘  │
│         │         │
│         ▼         │
│  ┌─────────────┐  │
│  │PaperTrading │  │ → Execute paper trades
│  └─────────────┘  │
└───────────────────┘
        │
        ▼
   WebSocket Manager → Broadcast to Frontend
```

**Public API:**
```python
async start()                           # Start service
async stop()                            # Stop service
get_latest_data(timeframe)              # Get latest candle
get_current_signals()                   # Get latest signal
get_candles(timeframe, limit)           # Get candle buffer
get_latest_indicators(timeframe)        # Get indicator values
get_historical_data_with_indicators()   # Get history + indicators
subscribe_signals(callback)             # Subscribe to signals
subscribe_updates(callback)             # Subscribe to updates
get_status()                            # Get service status
is_running()                            # Check if running
```

### 9.2 PaperTradingService (src/application/services/paper_trading_service.py)
**Vai trò:** Paper trading engine - Mô phỏng giao dịch Futures

**Features:**
- USDT-M Futures simulation
- Leverage support (default 1x)
- Position management (LONG/SHORT)
- Limit order execution
- Trailing stop logic
- Merge positions (One-way mode)
- TTL for pending orders (45 minutes)

**Key Methods:**
```python
on_signal_received(signal, symbol)      # Handle new signal
process_market_data(price, high, low)   # Check SL/TP/Liquidation
get_portfolio(current_price)            # Get portfolio state
get_trade_history(page, limit)          # Paginated history
calculate_performance(days)             # Performance metrics
get_settings() / update_settings()      # Settings management
execute_trade(signal, symbol)           # Execute trade
close_position(position, price, reason) # Close position
reset_account()                         # Reset to $10,000
```

**Position Lifecycle:**
```
Signal Received
      │
      ▼
┌─────────────┐
│   PENDING   │ ← Limit order waiting for fill
└─────────────┘
      │ Price hit entry
      ▼
┌─────────────┐
│    OPEN     │ ← Position active
└─────────────┘
      │ SL/TP/Liquidation/Manual
      ▼
┌─────────────┐
│   CLOSED    │ ← Position closed, PnL realized
└─────────────┘
```

### 9.3 SignalGenerator (src/application/signals/signal_generator.py)
**Vai trò:** Generate trading signals based on Trend Pullback strategy

**Strategy Logic:**
```
BUY Signal:
1. Trend: Price > VWAP (Bullish bias)
2. Setup: Pullback to Lower BB or VWAP
3. Trigger: StochRSI Cross Up (K > D, K < 80)
4. Confirmation: Green candle + Volume spike

SELL Signal:
1. Trend: Price < VWAP (Bearish bias)
2. Setup: Rally to Upper BB or VWAP
3. Trigger: StochRSI Cross Down (K < D, K > 20)
4. Confirmation: Red candle + Volume spike
```

**Signal Enrichment:**
```python
_enrich_signal():
1. Smart Entry Price (Limit order)
2. Stop Loss (ATR-based or Swing/EMA)
3. Take Profit (3 levels: TP1, TP2, TP3)
4. Position Size (Risk-based)
5. Confidence Score (with ADX penalty)
6. R:R Validation (min 0.8)
7. Volume Climax Filter (max 4.0x)
```

### 9.4 WebSocketManager (src/api/websocket_manager.py)
**Vai trò:** Manage WebSocket connections with Pub/Sub pattern

**Features:**
- Connection tracking per symbol (topic)
- Graceful disconnect handling
- Broadcast to all clients or by symbol
- Thread-safe operations
- Connection statistics

**Pattern:**
```
Publishers:
- RealtimeService (candle updates)
- SignalGenerator (trading signals)

Subscribers:
- Frontend WebSocket clients

Topics:
- Symbol names (e.g., 'btcusdt')
```

---

## 10. PHÂN TÍCH CHI TIẾT FRONTEND COMPONENTS

### 10.1 App.tsx - Main Layout
**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ HEADER (48px)                                               │
│ [Logo] [Nav: Chart|Portfolio|History|Settings] [Balance]    │
├─────────────────────────────────────────────────────────────┤
│ TICKER BAR (40px) - Only on Chart tab                       │
│ [BTC/USDT] [Price] [Change%] [H/L/RSI/VWAP] [Connection]   │
├─────────────────────────────────────────────────────────────┤
│ MAIN CONTENT                                                │
│ ┌─────────────────────────────────┬───────────────────────┐ │
│ │                                 │ RIGHT SIDEBAR (320px) │ │
│ │     CANDLE CHART                │ ┌───────────────────┐ │ │
│ │     (flex: 1)                   │ │ Strategy Monitor  │ │ │
│ │                                 │ ├───────────────────┤ │ │
│ │                                 │ │ Live Feed         │ │ │
│ │                                 │ │ (Signal Logs)     │ │ │
│ ├─────────────────────────────────┤ ├───────────────────┤ │ │
│ │ BOTTOM PANEL (176px)            │ │ Mode: PAPER       │ │ │
│ │ [Positions|Orders|History]      │ └───────────────────┘ │ │
│ └─────────────────────────────────┴───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**State:**
```typescript
- status: SystemStatus          // Backend status
- activeTab: Tab                // Current tab
- bottomTab: BottomTab          // Bottom panel tab
- isBottomPanelHidden: boolean  // Fullscreen mode
- signalLogs: SignalLog[]       // Live feed logs
```

### 10.2 CandleChart.tsx - Trading Chart
**Features:**
- TradingView Lightweight Charts integration
- VWAP overlay (yellow, linewidth: 2)
- Bollinger Bands overlay (blue)
- Volume histogram (bottom)
- Signal markers (green/red arrows)
- Dynamic price lines (Entry/SL/TP)
- Client-side candle aggregation
- Tooltip on signal hover
- Timeframe switching (1m/15m/1h)

**Series:**
```typescript
- candleSeries: Candlestick     // OHLC candles
- volumeSeries: Histogram       // Volume bars
- vwapSeries: Line              // VWAP line
- bbUpperSeries: Line           // BB upper band
- bbLowerSeries: Line           // BB lower band
```

**Price Lines (Dynamic):**
```typescript
- entryPriceLine: IPriceLine    // Entry price (gray dotted)
- slPriceLine: IPriceLine       // Stop loss (red dashed)
- tpPriceLine: IPriceLine       // Take profit (green dashed)
```

### 10.3 useMarketData.ts - WebSocket Hook
**Features:**
- WebSocket connection management
- Auto-reconnect with exponential backoff (1s → 30s)
- Countdown timer for reconnect
- Manual reconnect button
- Data gap filling after reconnect
- Ping/pong keep-alive

**State:**
```typescript
- data: MarketData              // Latest candle data
- signal: Signal                // Latest trading signal
- isConnected: boolean          // Connection status
- error: string | null          // Error message
- reconnectState: ReconnectState // Reconnect info
```

**Backoff Formula:**
```typescript
delay = min(1000 * (2 ** retryCount), 30000)
// 1s → 2s → 4s → 8s → 16s → 30s (cap)
```

### 10.4 candleAggregator.ts - Client-Side Aggregation
**Purpose:** Aggregate 1m candles to 15m/1h on frontend

**Logic:**
```typescript
function aggregateCandle(incoming1m, currentCandle, timeframe):
    intervalSeconds = timeframe === '15m' ? 900 : 3600
    candleStartTime = floor(incoming1m.time / intervalSeconds) * intervalSeconds
    
    if currentCandle && currentCandle.time === candleStartTime:
        // Update existing candle
        return {
            ...currentCandle,
            high: max(currentCandle.high, incoming1m.high),
            low: min(currentCandle.low, incoming1m.low),
            close: incoming1m.close
        }
    else:
        // New candle
        return {
            time: candleStartTime,
            open: incoming1m.open,
            high: incoming1m.high,
            low: incoming1m.low,
            close: incoming1m.close
        }
```

---

## 11. API ENDPOINTS

### 11.1 System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/system/status` | Backend status, version, uptime |

### 11.2 Market
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/ws/stream/{symbol}` | Real-time candle stream |
| GET | `/ws/history/{symbol}` | Historical candles with indicators |
| GET | `/ws/status` | WebSocket manager stats |
| GET | `/ws/connections` | Active connections list |
| GET | `/market/history` | Historical data (REST) |

### 11.3 Trades
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trades/history` | Paginated trade history |
| GET | `/trades/performance` | Performance metrics |
| GET | `/trades/portfolio` | Current portfolio state |
| GET | `/trades/equity-curve` | Equity curve data |
| POST | `/trades/close/{id}` | Close position manually |
| POST | `/trades/reset` | Reset paper account |
| POST | `/trades/simulate` | Simulate BUY/SELL signal |

### 11.4 Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings` | Get current settings |
| POST | `/settings` | Update settings |
| GET | `/settings/strategy` | Strategy parameters (read-only) |

---

## 12. DATABASE SCHEMA

### 12.1 paper_trades
```sql
CREATE TABLE paper_trades (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,           -- 'LONG' | 'SHORT'
    status TEXT NOT NULL,         -- 'PENDING' | 'OPEN' | 'CLOSED' | 'CANCELLED'
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    leverage INTEGER DEFAULT 1,
    margin REAL NOT NULL,
    liquidation_price REAL,
    stop_loss REAL,
    take_profit REAL,
    highest_price REAL DEFAULT 0, -- For trailing stop
    lowest_price REAL DEFAULT 0,
    open_time TEXT NOT NULL,
    close_time TEXT,
    realized_pnl REAL,
    exit_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 12.2 settings
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 12.3 account
```sql
CREATE TABLE account (
    id INTEGER PRIMARY KEY,
    balance REAL NOT NULL DEFAULT 10000.0
);
```

---

## 13. PROPERTY-BASED TESTS MAPPING

| Property | Test File | Validates |
|----------|-----------|-----------|
| 1. Candle Aggregation | `candleAggregator.test.ts` | Req 2.5 |
| 2. Trade Persistence | `test_persistence_properties.py` | Req 4.3 |
| 3. PnL Calculation | `test_pnl_calculation_properties.py` | Req 4.4 |
| 4. Engine Stability | `test_stability_properties.py` | Req 5.2 |
| 5. API Completeness | `test_historical_api_properties.py` | Req 5.4 |
| 6. Settings Persistence | `test_settings_properties.py` | Req 6.3 |
| 7. Pagination | `test_pagination_properties.py` | Req 7.1 |
| 8. Performance Metrics | `test_performance_metrics_properties.py` | Req 7.3 |

---

## 14. KẾT LUẬN

### 14.1 Điểm mạnh
- Kiến trúc Clean Architecture rõ ràng
- Property-based testing coverage tốt
- WebSocket với auto-reconnect
- Paper trading engine đầy đủ tính năng
- Frontend Binance-style chuyên nghiệp

### 14.2 Điểm cần cải thiện
- Nhiều file duplicate cần xóa
- Streamlit code cũ cần archive
- Scripts cần tổ chức lại
- CandleChart.tsx quá dài (977 lines) - cần refactor
- Một số services có thể không dùng

### 14.3 Bước tiếp theo
1. Backup toàn bộ project
2. Xóa files duplicate và debug
3. Archive Streamlit code
4. Tổ chức lại tests và scripts
5. Refactor CandleChart.tsx
6. Chạy full test suite để verify
