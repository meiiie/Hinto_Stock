# 📋 HINTO STOCK BACKEND ARCHITECTURE REPORT v1.0

> **For Frontend Team Integration**  
> Generated: 2025-12-25  
> Prepared by: Backend Engineer AI  
> Based on: SOTA patterns from Google/Amazon/Netflix/Bloomberg (Dec 2025)

---

## 📖 TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [API Reference](#3-api-reference)
4. [WebSocket Events](#4-websocket-events)
5. [State Machine](#5-state-machine)
6. [Data Flows](#6-data-flows)
7. [Frontend Integration Guide](#7-frontend-integration-guide)
8. [Error Handling](#8-error-handling)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API** | FastAPI 0.109+ | REST + WebSocket |
| **Async Bridge** | EventBus (asyncio.Queue) | Sync→Async communication |
| **Real-time** | WebSocket Pub/Sub | Market data streaming |
| **Trading Engine** | PaperTradingService | Order/Position management |
| **State Management** | TradingStateMachine | 6-state FSM for lifecycle |
| **Signal Generation** | SignalGenerator (Layer 0+1) | HMM + Technical analysis |
| **Persistence** | SQLite | Orders, signals persistence |

### 1.2 Architecture Pattern

```
┌────────────────────────────────────────────────────────────────┐
│                    CLEAN ARCHITECTURE                           │
├────────────────────────────────────────────────────────────────┤
│  PRESENTATION (API Layer)                                       │
│  ├── FastAPI Routers (REST)                                     │
│  ├── WebSocketManager (Pub/Sub)                                 │
│  └── EventBus (Async Bridge)                                    │
├────────────────────────────────────────────────────────────────┤
│  APPLICATION (Orchestration)                                    │
│  ├── RealtimeService (Central Coordinator)                      │
│  ├── PaperTradingService (Trading Engine)                       │
│  ├── SignalGenerator (Signal Logic)                             │
│  └── TradingStateMachine (Lifecycle)                            │
├────────────────────────────────────────────────────────────────┤
│  DOMAIN (Pure Business Logic)                                   │
│  ├── Entities (Candle, TradingSignal, PaperPosition)            │
│  ├── Interfaces (IOrderRepository, ISignalRepository)           │
│  └── Value Objects (RegimeResult, SignalStatus)                 │
├────────────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE (Technical Details)                             │
│  ├── Binance WebSocket/REST clients                             │
│  ├── SQLite repositories                                        │
│  └── Technical indicators (VWAP, BB, StochRSI, HMM)             │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM COMPONENTS                            │
│                                                                  │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐ │
│  │   Binance   │───▶│          RealtimeService               │ │
│  │  WebSocket  │    │  (Orchestrator - 1237 lines)           │ │
│  └─────────────┘    │                                         │ │
│                     │  • Manages WebSocket lifecycle          │ │
│                     │  • Coordinates data aggregation         │ │
│                     │  • Triggers signal generation           │ │
│                     │  • Publishes events via EventBus        │ │
│                     └─────────────────────────────────────────┘ │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           ▼                  ▼                  ▼               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ SignalGenerator │ │PaperTradingServ │ │TradingStateMach │   │
│  │    (628 lines)  │ │  (551 lines)    │ │  (346 lines)    │   │
│  │                 │ │                 │ │                 │   │
│  │ Layer 0: HMM    │ │ • Order mgmt    │ │ • 6 states      │   │
│  │ Layer 1: VWAP+  │ │ • Position mgmt │ │ • Transitions   │   │
│  │   BB+StochRSI   │ │ • P&L tracking  │ │ • Event publish │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                     ┌─────────────────┐                         │
│                     │    EventBus     │                         │
│                     │  (306 lines)    │──────▶ WebSocketManager │
│                     │                 │        (Pub/Sub)        │
│                     │ • Thread-safe   │                         │
│                     │ • Async queue   │                         │
│                     └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   EVENT FLOW (Async Bridge)                      │
│                                                                  │
│   SYNC DOMAIN                        ASYNC API                   │
│   ────────────                       ─────────                   │
│                                                                  │
│   RealtimeService ──publish()── EventBus ──broadcast()──▶ WS    │
│        │                            │                            │
│   PaperTradingService              Queue                 Clients │
│        │                            │                            │
│   TradingStateMachine      _broadcast_worker()                   │
│                                     │                            │
│                            WebSocketManager                      │
│                                                                  │
│   Pattern: Producer-Consumer with asyncio.Queue                  │
│   Solves: Async/Sync callback mismatch                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. API REFERENCE

### 3.1 REST Endpoints

#### System Router (`/system`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/system/status` | Health check + system status |
| GET | `/system/debug/signal-check` | Debug: why signals not generating |

#### Market Router (`/market-rest`, `/stream`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/stream/{symbol}` | WebSocket for real-time data |
| GET | `/market-rest/history` | Historical candles with indicators |
| GET | `/market-rest/websocket-status` | WebSocket connection stats |
| GET | `/market-rest/connections` | Active connections list |

#### Trades Router (`/trades`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trades/history` | Paginated trade history |
| GET | `/trades/performance` | Performance metrics (win rate, PnL) |
| GET | `/trades/portfolio` | Current portfolio status |
| GET | `/trades/equity-curve` | Equity curve for charting |
| POST | `/trades/close/{position_id}` | Manually close position |
| POST | `/trades/execute/{position_id}` | Execute pending at market |
| POST | `/trades/simulate` | Debug: simulate signal |
| POST | `/trades/reset` | Reset paper trading account |

#### Signals Router (`/signals`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signals/history` | Paginated signal history |
| GET | `/signals/pending` | Get pending signals |
| GET | `/signals/{signal_id}` | Get signal by ID |
| GET | `/signals/order/{order_id}` | Get signal for order |
| POST | `/signals/{signal_id}/execute` | Execute pending signal |
| POST | `/signals/{signal_id}/mark-pending` | Mark as shown to user |
| POST | `/signals/{signal_id}/expire` | Manually expire signal |
| POST | `/signals/expire-stale` | Expire old signals |

#### Settings Router (`/settings`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings/trading` | Get trading settings |
| PUT | `/settings/trading` | Update trading settings |

### 3.2 Response Formats

#### Signal Object
```json
{
  "id": "uuid-string",
  "signal_type": "buy" | "sell" | "neutral",
  "status": "generated" | "pending" | "executed" | "expired" | "rejected",
  "confidence": 0.85,
  "confidence_level": "high" | "medium" | "low",
  "price": 97450.50,
  "entry_price": 97420.00,
  "stop_loss": 97100.00,
  "tp_levels": {
    "tp1": 97700.00,
    "tp2": 98000.00,
    "tp3": 98400.00
  },
  "position_size": 0.0103,
  "risk_reward_ratio": 2.45,
  "indicators": {
    "vwap": 97350.00,
    "bb_upper": 97800.00,
    "bb_lower": 96900.00,
    "stoch_rsi_k": 22.5,
    "regime": "trending_low_vol",
    "regime_confidence": 0.78
  },
  "reasons": ["Price above VWAP", "StochRSI oversold"],
  "generated_at": "2025-12-25T21:55:00Z",
  "pending_at": null,
  "executed_at": null,
  "order_id": null,
  "execution_latency_ms": null
}
```

#### Portfolio Object
```json
{
  "wallet_balance": 10000.00,
  "margin_balance": 10125.50,
  "available_balance": 9800.00,
  "unrealized_pnl": 125.50,
  "total_equity": 10125.50,
  "open_positions": [
    {
      "id": "uuid-string",
      "symbol": "BTCUSDT",
      "side": "LONG",
      "status": "OPEN",
      "entry_price": 97000.00,
      "size": 0.0103,
      "leverage": 1,
      "current_pnl": 125.50,
      "current_pnl_pct": 1.25,
      "stop_loss": 96700.00,
      "take_profits": [97300, 97600, 97900],
      "entry_time": "2025-12-25T20:30:00Z"
    }
  ],
  "pending_orders": []
}
```

---

## 4. WEBSOCKET EVENTS

### 4.1 Event Types

| Event Type | Payload | Description |
|------------|---------|-------------|
| `candle` | CandleData | New/updated candle with indicators |
| `signal` | SignalData | New trading signal generated |
| `state_change` | StateData | State machine transition |
| `status` | StatusData | System status update |
| `error` | ErrorData | Error notification |

### 4.2 Event Payloads

#### Candle Update Event
```json
{
  "type": "candle",
  "symbol": "btcusdt",
  "timestamp": "2025-12-25T21:55:00Z",
  "data": {
    "open": 97400.00,
    "high": 97500.00,
    "low": 97380.00,
    "close": 97450.00,
    "volume": 125.5,
    "timestamp": "2025-12-25T21:55:00Z",
    "is_closed": true,
    "timeframe": "1m",
    "indicators": {
      "vwap": 97350.00,
      "bb_upper": 97800.00,
      "bb_middle": 97350.00,
      "bb_lower": 96900.00,
      "stoch_rsi_k": 45.5,
      "stoch_rsi_d": 42.0,
      "adx": 28.5,
      "atr": 150.00
    }
  }
}
```

#### Signal Event
```json
{
  "type": "signal",
  "symbol": "btcusdt",
  "timestamp": "2025-12-25T21:55:30Z",
  "data": {
    "id": "uuid-string",
    "signal_type": "buy",
    "confidence": 0.82,
    "price": 97450.00,
    "entry_price": 97420.00,
    "stop_loss": 97100.00,
    "tp_levels": {"tp1": 97700, "tp2": 98000, "tp3": 98400},
    "reasons": ["Price above VWAP", "StochRSI oversold cross"]
  }
}
```

#### State Change Event
```json
{
  "type": "state_change",
  "symbol": "btcusdt",
  "timestamp": "2025-12-25T21:55:35Z",
  "data": {
    "from_state": "SCANNING",
    "to_state": "ENTRY_PENDING",
    "reason": "BUY signal generated",
    "order_id": "uuid-string",
    "position_id": null
  }
}
```

### 4.3 WebSocket Connection

```typescript
// Frontend connection example
const ws = new WebSocket('ws://localhost:8000/stream/btcusdt');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'candle':
      updateChart(data.data);
      break;
    case 'signal':
      showSignalNotification(data.data);
      break;
    case 'state_change':
      updateSystemState(data.data);
      break;
  }
};
```

---

## 5. STATE MACHINE

### 5.1 State Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │              TRADING STATE MACHINE                   │
                    │                                                      │
                    │   ┌──────────┐                                       │
                    │   │BOOTSTRAP │─── warm-up complete ───▶┌──────────┐ │
                    │   │ (init)   │                         │ SCANNING │ │
                    │   └──────────┘                         │ (ready)  │ │
                    │        │                               └────┬─────┘ │
                    │   load failed                              │        │
                    │        │                          signal generated  │
                    │        ▼                                   │        │
                    │   ┌──────────┐                             ▼        │
                    │   │  HALTED  │◀────────────────────┌─────────────┐  │
                    │   │ (error)  │     critical error  │ENTRY_PENDING│  │
                    │   └──────────┘                     │(order placed)│  │
                    │        ▲                           └──────┬──────┘  │
                    │        │                                  │         │
                    │   any error                         order filled    │
                    │        │                                  │         │
                    │   ┌────┴─────┐     cooldown done    ┌─────▼──────┐  │
                    │   │ COOLDOWN │◀─────────────────────│IN_POSITION │  │
                    │   │(rest 4x) │                      │  (active)  │  │
                    │   └──────────┘                      └────────────┘  │
                    │                                                      │
                    └──────────────────────────────────────────────────────┘
```

### 5.2 State Definitions

| State | Description | Trading Allowed | Next States |
|-------|-------------|-----------------|-------------|
| `BOOTSTRAP` | Loading historical data | ❌ | SCANNING, HALTED |
| `SCANNING` | Waiting for signals | ✅ Signals only | ENTRY_PENDING, HALTED |
| `ENTRY_PENDING` | Order placed | ❌ | IN_POSITION, SCANNING, HALTED |
| `IN_POSITION` | Active position | ❌ New signals | COOLDOWN, HALTED |
| `COOLDOWN` | Rest period (4 candles) | ❌ | SCANNING, HALTED |
| `HALTED` | Error state | ❌ Terminal | None |

### 5.3 Frontend State Sync

```typescript
interface SystemState {
  state: 'BOOTSTRAP' | 'SCANNING' | 'ENTRY_PENDING' | 'IN_POSITION' | 'COOLDOWN' | 'HALTED';
  canReceiveSignals: boolean;
  isActiveTrade: boolean;
  cooldownRemaining: number;
  currentOrderId: string | null;
  currentPositionId: string | null;
}
```

---

## 6. DATA FLOWS

### 6.1 Signal Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   SIGNAL GENERATION FLOW                         │
│                                                                  │
│   Binance WS ──candle──▶ RealtimeService                        │
│                              │                                   │
│                   ┌──────────▼──────────┐                        │
│                   │   _generate_signals  │                       │
│                   └──────────┬──────────┘                        │
│                              │                                   │
│              ┌───────────────▼───────────────┐                   │
│              │        SignalGenerator         │                  │
│              │                                │                  │
│              │  ┌─────────────────────────┐  │                   │
│              │  │ LAYER 0: Regime Filter  │  │                   │
│              │  │    (HMM Detection)      │  │                   │
│              │  │                         │  │                   │
│              │  │  RANGING? ──▶ BLOCK ❌  │  │                   │
│              │  │  TRENDING? ──▶ PASS ✅  │  │                   │
│              │  └─────────────────────────┘  │                   │
│              │               │               │                   │
│              │  ┌────────────▼────────────┐  │                   │
│              │  │ LAYER 1: Signal Logic   │  │                   │
│              │  │   VWAP + BB + StochRSI  │  │                   │
│              │  │   + ADX + Volume         │  │                   │
│              │  └─────────────────────────┘  │                   │
│              │               │               │                   │
│              │  ┌────────────▼────────────┐  │                   │
│              │  │ ENRICHMENT:              │  │                   │
│              │  │  • Smart Entry Price     │  │                   │
│              │  │  • TP1/TP2/TP3 levels    │  │                   │
│              │  │  • Stop Loss (ATR-based) │  │                   │
│              │  │  • Position Size         │  │                   │
│              │  │  • Confidence Score       │  │                   │
│              │  └─────────────────────────┘  │                   │
│              └───────────────┬───────────────┘                   │
│                              │                                   │
│                              ▼                                   │
│              ┌───────────────────────────────┐                   │
│              │  SignalLifecycleService       │                   │
│              │  • Register signal (UUID)     │                   │
│              │  • Persist to SQLite          │                   │
│              └───────────────┬───────────────┘                   │
│                              │                                   │
│              ┌───────────────▼───────────────┐                   │
│              │       EventBus.publish()       │                  │
│              │  event_type: "signal"          │                  │
│              └───────────────┬───────────────┘                   │
│                              │                                   │
│                              ▼                                   │
│              WebSocketManager.broadcast() ──▶ Frontend           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Trade Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADE EXECUTION FLOW                          │
│                                                                  │
│   Signal Generated                                               │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────┐                   │
│   │ StateMachine: SCANNING → ENTRY_PENDING  │                   │
│   └─────────────────────────────────────────┘                   │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────┐                   │
│   │ PaperTradingService.on_signal_received  │                   │
│   │                                         │                   │
│   │ 1. Check balance                        │                   │
│   │ 2. Check position limit                 │                   │
│   │ 3. Calculate margin                     │                   │
│   │ 4. Create PENDING order                 │                   │
│   └─────────────────────┬───────────────────┘                   │
│                         │                                        │
│        ┌────────────────┼────────────────┐                      │
│        ▼                ▼                ▼                      │
│   Price hits entry  TTL expires    Manual cancel                │
│        │                │                │                      │
│        ▼                ▼                ▼                      │
│   Order FILLED      Order EXPIRED    Order CANCELLED            │
│        │                │                │                      │
│        ▼                └────────┬───────┘                      │
│   ┌────────────┐                 │                              │
│   │ Position   │     Back to SCANNING                           │
│   │   OPEN     │                                                │
│   └─────┬──────┘                                                │
│         │                                                        │
│   ┌─────▼─────────────────────────────────┐                     │
│   │ StateMachine: ENTRY_PENDING → IN_POS  │                     │
│   └───────────────────────────────────────┘                     │
│         │                                                        │
│   process_market_data() watches for:                            │
│   ┌─────┴────────────────────┬──────────────────┐               │
│   ▼                          ▼                  ▼               │
│   Stop Loss hit         TP1/TP2/TP3 hit     Liquidation         │
│   (full close)          (partial close)     (full close)        │
│        │                     │                  │               │
│        └─────────────────────┴──────────────────┘               │
│                              │                                   │
│                              ▼                                   │
│        ┌─────────────────────────────────────────┐              │
│        │ StateMachine: IN_POSITION → COOLDOWN    │              │
│        │         (4 candles rest period)         │              │
│        └─────────────────────────────────────────┘              │
│                              │                                   │
│                      tick_cooldown()                            │
│                              │                                   │
│                              ▼                                   │
│        ┌─────────────────────────────────────────┐              │
│        │ StateMachine: COOLDOWN → SCANNING       │              │
│        │         (ready for new signals)         │              │
│        └─────────────────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. FRONTEND INTEGRATION GUIDE

### 7.1 Recommended Hooks Structure

```typescript
// hooks/useMarketData.ts
// Subscribe to real-time candle data via WebSocket

// hooks/useSignals.ts  
// Subscribe to signal events + fetch signal history

// hooks/usePortfolio.ts
// Fetch portfolio status + open positions

// hooks/useSystemState.ts
// Subscribe to state changes + display current state

// hooks/useTradeHistory.ts
// Paginated trade history with performance metrics
```

### 7.2 Data Refresh Strategy

| Data Type | Source | Refresh Strategy |
|-----------|--------|------------------|
| Candles | WebSocket | Real-time push |
| Signals | WebSocket + REST | Push + polling backup |
| Portfolio | REST | Poll every 5s |
| Trade History | REST | On-demand + after trade |
| System State | WebSocket | Real-time push |

### 7.3 Critical UI Components

1. **Candlestick Chart** - Subscribe to `candle` events
2. **Signal Indicator** - Overlay on chart when `signal` received
3. **State Badge** - Show current state (SCANNING/IN_POSITION etc)
4. **Portfolio Panel** - Balance, equity, unrealized P&L
5. **Position Card** - Open positions with SL/TP levels
6. **Trade History Table** - Paginated with filters
7. **Signal History** - With status tracking (executed/expired)

---

## 8. ERROR HANDLING

### 8.1 HTTP Error Codes

| Code | Meaning | Frontend Action |
|------|---------|-----------------|
| 200 | Success | Process response |
| 400 | Bad request | Show validation error |
| 404 | Not found | Show "not found" message |
| 500 | Server error | Show error + retry button |
| 503 | Service unavailable | Show "connecting..." |

### 8.2 WebSocket Reconnection

```typescript
// Recommended reconnection strategy
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000]; // Exponential backoff

ws.onclose = () => {
  // 1. Show "Reconnecting..." status
  // 2. Attempt reconnect with backoff
  // 3. Fetch missed data via REST after reconnect
};
```

### 8.3 State Machine Error Recovery

When `state_change` event shows `to_state: "HALTED"`:
- Display prominent error banner
- Show halt reason
- Provide "Acknowledge & Resume" button (call reset endpoint)

---

## APPENDIX A: Quick Reference

### API Base URL
```
http://localhost:8000
```

### WebSocket URL
```
ws://localhost:8000/stream/{symbol}
```

### Key Endpoints for MVP
1. `GET /trades/portfolio` - Dashboard main data
2. `WS /stream/btcusdt` - Real-time streaming
3. `GET /signals/pending` - Actionable signals
4. `POST /signals/{id}/execute` - Execute signal
5. `GET /trades/history` - Trade log

---

*Document maintained by Backend Engineer AI*
