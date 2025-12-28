# Hinto Trader Pro 📈

**Professional Desktop Trading Application**

**Version:** 2.1 | **Status:** 🚀 Production Ready  
**Strategy:** Trend Pullback (VWAP + Bollinger Bands + StochRSI)  
**Market:** Multi-Token (BTC, ETH, SOL, BNB, TAO, FET, ONDO) × Multi-Timeframe (1m, 15m, 1h)

---

## ✨ Key Features (Dec 2025)

- **🎯 SOTA Multi-Token Trading** - 7 crypto tokens with Combined Streams (1 WebSocket = 21 streams)
- **🚀 SOTA Multi-Timeframe Streaming** - Real-time updates every 250ms for 1m, 15m, 1h
- **📦 Hybrid Data Layer** - SQLite persistence + Binance fallback (zero data loss on restart)
- **🎨 Binance-Style UI** - Professional dark theme with token icons + TokenSelector
- **📊 Advanced Charts** - TradingView Lightweight Charts with VWAP, BB, signals
- **⚡ State Machine** - BOOTSTRAP → SCANNING → IN_POSITION → COOLDOWN
- **📱 Desktop App** - Tauri-powered native desktop application

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Project Architecture](documents/PROJECT_ARCHITECTURE.md) | System design and trading logic |
| [Frontend Architecture](frontend/README.md) | React/TypeScript desktop UI |
| [API Documentation](src/api/README.md) | FastAPI backend endpoints |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or pnpm

### 1. Backend Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m uvicorn src.api.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Development mode
npm run dev

# Production build
npm run build
```

### 3. Run Tests
```bash
# Backend tests
pytest tests/

# Architecture compliance
pytest tests/architecture/ -v
```

---

## 🏗️ Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Frontend      │  │   Backend API   │                   │
│  │   (React/TS)    │  │   (FastAPI)     │                   │
│  │   + Tauri       │  │   + WebSocket   │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ SignalGenerator │  │ RealtimeService │                   │
│  │ StateMachine    │  │ EventBus        │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │    Entities     │  │   Interfaces    │                   │
│  │ (Candle, Signal)│  │ (Repositories)  │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
            ▲                    ▲
            │                    │
┌───────────┴────────────────────┴────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Indicators    │  │   Persistence   │                   │
│  │ (VWAP, BB, RSI) │  │   (SQLite)      │                   │
│  └─────────────────┘  └─────────────────┘                   │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   WebSocket     │  │   REST Client   │                   │
│  │ (Multi-Stream)  │  │   (Binance)     │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### SOTA Multi-Token Architecture (Dec 2025)

**Following Binance Official Best Practices:**

| Feature | Implementation |
|---------|---------------|
| Combined Streams | 1 WebSocket for ALL symbols (7 × 3 = 21 streams) |
| Max Streams | 1024 per connection (we use 21) |
| Message Rate | < 5/second (compliant) |
| Connection Lifetime | Auto-reconnect before 24h |

```
┌─────────────────────────────────────────────────────────────────┐
│                  SharedBinanceClient (Singleton)                 │
│       wss://stream.binance.com/stream?streams=                  │
│  btcusdt@kline_1m/ethusdt@kline_1m/solusdt@kline_1m/...        │
│                     (1 WebSocket = 21 streams)                   │
└─────────────────────────────────────────────────────────────────┘
                               ↓ routes by symbol
       ┌───────────────────────┼───────────────────────┐
       ↓                       ↓                       ↓
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ RealtimeService      │  RealtimeService     │  RealtimeService
│   BTCUSDT    │       │    ETHUSDT   │       │    SOLUSDT   │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       ↓                       ↓                       ↓
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ SignalGenerator      │  SignalGenerator     │  SignalGenerator
└──────────────┘       └──────────────┘       └──────────────┘
```

**Supported Tokens (configurable via env):**
- BTC, ETH, SOL, BNB, TAO, FET, ONDO (default 7)
- Scalable to 100+ tokens (1024 stream limit)

**Key Files:**
- `SharedBinanceClient` - `src/infrastructure/websocket/shared_binance_client.py`
- `MultiTokenConfig` - `src/config.py`
- `TokenSelector` - `frontend/src/components/TokenSelector.tsx`

### 📦 SOTA Hybrid Data Layer (Dec 2025)

**Problem:** Data lost on backend restart, slow Binance API calls.

**Solution:** Read-through cache pattern with 3 layers:

```
┌─────────────────────────────────────────┐
│           REST API / Startup            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  L1: In-Memory (deques)                 │  ← Fastest, volatile
├─────────────────────────────────────────┤
│  L2: SQLite (80% threshold)             │  ← Fast, persistent
├─────────────────────────────────────────┤
│  L3: Binance REST API (fallback)        │  ← Slow, source of truth
└─────────────────────────────────────────┘
```

| Scenario | Before | After |
|----------|--------|-------|
| First startup | Binance only | Binance + save to SQLite |
| Restart with data | Binance only | SQLite first (fast) |
| Binance API down | No data | Use SQLite cache |

### 🧠 SOTA Strategy Configuration (Dec 2025)

**Problem:** Hardcoded strategy parameters caused near-zero signal generation.

**Solution:** Centralized `StrategyConfig` dataclass with environment-based tuning:

| Parameter | Before | After (SOTA) |
|-----------|--------|--------------|
| `strict_mode` | True (4/5) | **False** (3/5) |
| `regime_filter` | Hard block | **Penalty mode** (-30%) |
| `bb_threshold` | 1.5% | **2.5%** |
| `vwap_threshold` | 1.0% | **2.0%** |
| `stoch_oversold` | 20 | **30** |

**Key Components:**
- `StrategyConfig` - Centralized in `config.py`
- `ConfluenceScorer` - Weighted signal scoring (60% threshold)
- `RegimeDetector` - ADX-based with configurable threshold

**Environment Variables:**
```env
STRATEGY_STRICT_MODE=false
STRATEGY_REGIME_FILTER_MODE=penalty
STRATEGY_BB_THRESHOLD_PCT=0.025
```

---

## 🛠️ Project Structure

```
Hinto_Stock/
├── src/
│   ├── domain/             # Entities, Interfaces
│   ├── application/        # Services, Signal Generation
│   ├── infrastructure/     # Indicators, WebSocket, Persistence
│   └── api/                # FastAPI Backend + EventBus
├── frontend/
│   ├── src/
│   │   ├── components/     # React Components (CandleChart, TokenIcon)
│   │   ├── hooks/          # useMarketData (WebSocket)
│   │   └── styles/         # theme.ts, layout.css
│   └── src-tauri/          # Tauri Desktop Config
├── tests/
│   ├── architecture/       # Clean Architecture tests
│   └── unit/               # Unit tests
├── scripts/                # Utility Scripts
└── documents/              # Documentation
```

---

## 🎨 Frontend Features

### Token Icons
Uses `@web3icons/react` library for professional crypto icons:
```tsx
import { TokenIcon } from './components/TokenIcon';
<TokenIcon symbol="BTC" size={24} />
```

### Real-Time Price Display
- Header syncs with chart timeframe
- Multi-timeframe WebSocket support
- Tick-by-tick updates (250ms)

### Theme System
```typescript
THEME.spacing.md  // 16px
THEME.sizing.chart.minHeight  // 400px
THEME.status.buy  // #0ECB81
```

---

## 📊 Trading Strategy

### Trend Pullback Strategy (v2.1)
1.  **Trend Detection:**
    *   **Layer 1 (HTF):** 1H Trend Direction (EMA50) - *Global Filter*
    *   **Layer 2 (Intraday):** Price vs VWAP - *Local Trend*
2.  **Entry:**
    *   **Setup:** Pullback to BB Lower/VWAP
    *   **Trigger:** StochRSI Cross Up (< 30)
    *   **Confluence:** Must align with 1H Trend (e.g., Buy only if 1H is Bullish)
3.  **Exit:** StochRSI overbought (> 80) or TP/SL hit

### Risk Management
- Stop Loss: -1% from entry
- Take Profit: Dynamic (1.5x-3x risk)
- Position Size: Fixed or % of balance

---

## 🎯 Goals

Build a professional-grade, automated trading system with:
- **Clean Architecture** for maintainability
- **SOTA UI/UX** following Binance patterns
- **Real-time data** via WebSocket streams
- **Consistent profits** through statistical edge

---

## 📝 License

MIT License - See LICENSE file for details.
