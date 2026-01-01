# 🌐 GLOBAL ARCHITECTURE - Hinto Stock Trading System

**Document Version:** 1.1
**Last Updated:** 2025-12-29
**Maintainer:** Project Manager AI

---

## 1. SYSTEM OVERVIEW

**Hinto Stock** là nền tảng trading cryptocurrency 24/7 với kiến trúc **3-layer hybrid**, được xây dựng dưới dạng Desktop Application.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DESKTOP APP (Electron/Tauri)               │
├─────────────────────────────────────────────────────────────────────┤
│                            PRESENTATION LAYER                       │
│                        (React + TailwindCSS UI)                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ IPC/Events
┌───────────────────────────────────▼─────────────────────────────────┐
│                          APPLICATION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Layer 3     │  │ Layer 2     │  │ Layer 1     │  │ Risk        │  │
│  │ LLM Planner │  │ Candle      │  │ Real-time   │  │ Management  │  │
│  │ (30m-1h)    │  │ Confirmer   │  │ Signals     │  │ System      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ Domain Events
┌───────────────────────────────────▼─────────────────────────────────┐
│                            DOMAIN LAYER                             │
│  (Entities, Value Objects, Domain Services, Repository Interfaces)  │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ Repositories
┌───────────────────────────────────▼─────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                         │
│  (Binance API, SQLite DB, WebSocket, TA-Lib, DI Container, Logging) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 3-LAYER SIGNAL ARCHITECTURE

### Layer 1: Real-time Trading Signals (Core)
| Indicator | Formula | Purpose |
|-----------|---------|---------|
| **VWAP** | ∑(Price × Volume) / ∑Volume | Trend direction filter |
| **Bollinger Bands** | SMA(20) ± 2σ | Volatility envelope |
| **StochRSI** | (RSI - min(RSI)) / (max(RSI) - min(RSI)) | Entry trigger |

**Buy Signal Logic:**
```
Price > VWAP (Uptrend confirmed)
AND Price touches Lower BB OR VWAP (Pullback zone)
AND StochRSI crosses above 20 (Momentum shift)
AND Volume > Previous Red Candle Volume (Buying pressure)
```

### Layer 2: Institutional Confirmation (SOTA)
- **SFP Detector:** Swing Failure Pattern detection (Zero Lag Entry)
- **Volume Delta:** Order Flow approximation (Buy/Sell Pressure)
- **Momentum Velocity:** FOMO Filter (Blocks signals if price moves too fast)
- **Liquidity Zones:** Stop Hunt Protection (Smart SL placement)

### Layer 3: LLM Strategic Planning
- Market regime analysis
- Risk profile adjustment
- News sentiment (future)

---

## 3. TECHNOLOGY STACK

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.x |
| Build Tool | Vite | 5.x |
| Styling | TailwindCSS | 3.x |
| State | Zustand | 4.x |
| Charts | Lightweight Charts | 4.x |
| Desktop | Electron/Tauri | Latest |

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Async | asyncio + aiohttp | - |
| Validation | Pydantic | 2.x |
| DI | dependency-injector | 4.x |
| Exchange | ccxt | Latest |

### Data
| Component | Technology | Notes |
|-----------|-----------|-------|
| Primary DB | SQLite | Desktop deployment |
| Cache | In-memory | Indicator calculations |
| Queue | asyncio.Queue | Internal message passing |

---

## 4. DATA FLOW

```
[Binance WebSocket]
        │
        ▼
┌───────────────────┐
│  Price Aggregator │ ← Raw OHLCV tick data
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Indicator Engine  │ ← Calculate VWAP, BB, StochRSI
└─────────┬─────────┘
          │
          ├──────────────────┐
          ▼                  ▼
┌─────────────────┐  ┌───────────────────┐
│ Signal Generator│  │ Pattern Detector  │
│   (Layer 1)     │  │   (Layer 2)       │
└────────┬────────┘  └─────────┬─────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────┐
│            Signal Aggregator            │
│   (Combine Layer 1 + 2, apply rules)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│            Risk Manager                 │
│   (Position sizing, SL/TP, margin)      │
└────────────────┬────────────────────────┘
                 │
                 ├─────────────────┐
                 ▼                 ▼
         ┌─────────────┐   ┌─────────────┐
         │ Order Queue │   │   UI Layer  │
         │  (Execute)  │   │  (Display)  │
         └─────────────┘   └─────────────┘
```

---

## 5. EVENT BUS ARCHITECTURE

### Event Types
```typescript
// Core events
type EventType = 
  | 'price:update'       // Raw price tick
  | 'candle:close'       // Candle completed
  | 'indicator:update'   // Indicator recalculated
  | 'signal:new'         // New trading signal
  | 'signal:expired'     // Signal no longer valid
  | 'position:open'      // Trade executed
  | 'position:close'     // Position closed
  | 'risk:alert'         // Risk threshold reached
  | 'system:error';      // System error
```

### Event Flow
```
[Producer] → EventBus → [Consumer 1]
                    → [Consumer 2]
                    → [Consumer N]
```

---

## 6. DIRECTORY STRUCTURE

```
Hinto_Stock/
├── app/
│   ├── frontend/           # React UI
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── services/
│   │   └── package.json
│   │
│   └── backend/            # Python backend
│       ├── domain/
│       │   ├── entities/
│       │   ├── services/
│       │   └── value_objects/
│       ├── application/
│       │   ├── use_cases/
│       │   └── dtos/
│       ├── infrastructure/
│       │   ├── exchanges/
│       │   ├── repositories/
│       │   └── websocket/
│       └── main.py
│
├── documents/              # AI Agent System
│   ├── agents/
│   ├── shared-context/
│   ├── communication/
│   └── workflows/
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 7. AI AGENT COGNITIVE FRAMEWORK

### SOTA Techniques Applied

| Technique | Source | Usage |
|-----------|--------|-------|
| **Meta-Prompting** | Stanford/OpenAI | PM as Conductor orchestrating expert agents |
| **ReAct Pattern** | Google Research | Thought → Action → Observation loop |
| **Chain-of-Thought** | Various | "Think step-by-step" for complex reasoning |
| **PTCF Framework** | Google Gemini | Persona-Task-Context-Format structure |
| **XML Tags** | Anthropic | Structured prompt sections |

### Agent Interaction Protocol

```
             Human Owner
                  ↓
        [Project Manager AI]  ← Meta-Conductor
                  ↓
    ╔═══════════════════════════════════╗
    ║  ReAct Loop for Each Task         ║
    ╠═══════════════════════════════════╣
    ║  <thought> Analyze situation      ║
    ║  <action>  Execute or delegate    ║
    ║  <observation> Process results    ║
    ╚═══════════════════════════════════╝
                  ↓
    ┌─────────┬─────────┬─────────┐
    ↓         ↓         ↓         ↓
Frontend  Backend  Database    QA
    ↓         ↓         ↓         ↓
    └─────────┴─────────┴─────────┘
              Collaboration
```

### Trigger Commands

| Command | Effect |
|---------|--------|
| (Default) | Standard concise response |
| `ULTRATHINK` | Deep multi-dimensional analysis |
| `Think step-by-step` | Chain-of-Thought reasoning |
| `<thinking>` | Explicit internal reasoning block |

### Context Loading Order
```
1. agents/{role}/system-prompt.md  ← Primary identity
2. shared-context/global-architecture.md  ← This file
3. agents/{role}/context/progress.md  ← Session continuity
4. (Task-specific context as needed)
```

---

## 8. KEY METRICS TARGETS

| Metric | Target | Rationale |
|--------|--------|-----------|
| Win Rate | > 70% | Improved via SFP & Volume Delta |
| Risk/Reward | > 1:2.0 | Optimized via Liquidity Zones |
| Max Drawdown | < 10% | Protected by Velocity Filter |
| Profit Factor | > 2.0 | Gross Profit / Gross Loss |
| Latency | < 50ms | SFP Zero Lag Entry |

---

## 8. CURRENT STATUS

**Phase:** ✅ Layer 1 Complete → 🔄 Algorithm Improvement

| Component | Status | Owner |
|-----------|--------|-------|
| Layer 1 Core | 🟢 Complete | Backend |
| UI Dashboard | 🟢 Complete | Frontend |
| Chart Display | 🟢 Complete (BBFillPlugin) | Frontend |
| Signal Display | 🟢 Complete | Frontend |
| Database | 🟢 Stable | Database |
| Testing | 🟡 Partial | QA |
| **Algorithm Improvement** | **🔄 Next Phase** | **Quant Specialist** |

---

## 9. CHANGE LOG

| Date | Change | Author |
|------|--------|--------|
| 2025-12-22 | Initial architecture document | Project Manager AI |
| 2025-12-29 | Updated status: Layer 1 Complete, Algorithm phase next | AI Assistant |

---

**IMPORTANT:** This document is the single source of truth for system architecture. All agents MUST read this before starting any work.
