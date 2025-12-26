# Hinto Trader Pro 📈

**Professional Desktop Trading Application**

**Version:** 2.0 | **Status:** 🚀 Production Ready  
**Strategy:** Trend Pullback (VWAP + Bollinger Bands + StochRSI)  
**Market:** BTC/USDT Futures (Multi-Timeframe: 1m, 15m, 1h)

---

## ✨ Key Features (Dec 2025)

- **🚀 SOTA Multi-Timeframe Streaming** - Real-time updates every 250ms for 1m, 15m, 1h
- **📦 Hybrid Data Layer** - SQLite persistence + Binance fallback (zero data loss on restart)
- **🎨 Binance-Style UI** - Professional dark theme with token icons
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

### SOTA Multi-Timeframe Architecture

```
Binance WebSocket (Combined Streams)
  wss://stream.binance.com:9443/stream?streams=
    btcusdt@kline_1m/btcusdt@kline_15m/btcusdt@kline_1h
                          ↓
              BinanceWebSocketClient
              (parses stream → interval)
                          ↓
                  RealtimeService
              (routes by interval)
                    ↓   ↓   ↓
                   1m  15m  1h
                    ↓   ↓   ↓
                    EventBus
                    ↓   ↓   ↓
                   Frontend
```

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

### Trend Pullback Strategy
1. **Trend Detection:** ADX > 25, VWAP trend alignment
2. **Entry:** StochRSI oversold (< 20) + BB Lower touch
3. **Exit:** StochRSI overbought (> 80) or TP/SL hit

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
