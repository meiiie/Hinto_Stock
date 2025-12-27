# SHARED BOARD - Inter-Agent Collaboration Space

Version: 1.2 | Updated: 2025-12-27

This is the central shared memory for all AI agents. Update this file when:
- Making decisions that affect other agents
- Completing work that others depend on
- Discovering blockers or issues
- Changing shared resources (APIs, schemas, etc.)

---

## CURRENT SPRINT STATUS

Phase: SOTA Strategy Config ✅
Sprint: 2025-W52
Focus: Signal Generation + Trade Execution Flow - COMPLETE

### Active Work

| Agent | Current Task | Status | Blockers | Last Updated |
|-------|--------------|--------|----------|--------------|
| PM | System setup | Complete | None | 2025-12-22 |
| FE | Execute button fix | ✅ Complete | None | 2025-12-22 |
| BE | **SOTA Strategy Config** | **✅ Complete** | None | **2025-12-27** |
| BE | **Signal Flow Fix** | **✅ Complete** | None | **2025-12-27** |
| DB | Codebase audit | Complete | None | 2025-12-22 |
| QA | Codebase audit | Complete | None | 2025-12-22 |
| QS | Initial setup | ✅ Ready | None | 2025-12-23 |


---

## CODEBASE STATUS (Actual)

### Backend (src/)
```
STATUS: IMPLEMENTED - Clean Architecture
Layers: API / Application / Domain / Infrastructure

Key Components:
- FastAPI app with WebSocket support
- RealtimeService (1000+ lines) - Main orchestrator
- 8 Indicators: VWAP, BB, StochRSI, ADX, ATR, SwingPoint, VolumeSpike, TaLib
- Paper Trading Service
- State Machine (BOOTSTRAP/SCANNING/POSITION_OPEN)
- EventBus for async communication
```

### Frontend (frontend/)
```
STATUS: IMPLEMENTED - Trading Dashboard
Stack: React 19 + Vite 7 + TailwindCSS 4 + Tauri 2

Key Components:
- CandleChart (977 lines) - Lightweight Charts with VWAP/BB overlays
- useMarketData hook - WebSocket with exponential backoff
- 10 trading components: Portfolio, Settings, TradeHistory, SignalCard...
- Binance-style dark theme
```

---

## DECISIONS LOG

### [DECISION-001] Multi-Agent System Structure
Date: 2025-12-22
Made By: Human Owner + PM
Affects: All agents
Decision: Adopt SOTA 2025 prompt engineering with XML tags, ReAct, CoT
Status: Implemented

### [DECISION-002] Clean Architecture Backend
Date: 2025-12-22
Made By: BE (historical)
Affects: BE, DB
Decision: 4-layer Clean Architecture (API/App/Domain/Infra)
Status: Already Implemented

### [DECISION-003] SOTA Strategy Configuration Architecture
Date: 2025-12-27
Made By: BE + Human Owner
Affects: BE, Signal Generation, Trade Execution
Decision: 
- Centralized StrategyConfig dataclass with environment-based tuning
- Regime penalty mode (replace hard block)
- ConfluenceScorer for weighted signal scoring (60% threshold)
- PaperTradingService injection into RealtimeService for signal→trade flow
Status: Implemented

---

## PENDING HANDOFFS

| From | To | Task | Priority | Created | Status |
|------|-----|------|----------|---------|--------|
| - | - | No pending handoffs | - | - | - |

---

## SHARED RESOURCES

### API Contracts
Location: agents/backend-engineer/context/api-contracts.md
Last Updated: 2025-12-22
Status: Needs update from actual code

Actual Endpoints (from codebase):
- GET / - Health check
- WS /ws/market - Real-time data
- GET /market/candles - Historical data
- GET /trades/history - Trade history
- GET/PUT /settings - App settings

### Database Schema
Location: agents/database-specialist/context/schema-evolution.md
Status: Draft - needs update from actual persistence layer

### Design System
Location: agents/frontend-architect/context/design-system.md
Status: Draft

### Test Strategy
Location: agents/qa-engineer/context/test-strategy.md
Status: Draft

---

## KNOWN ISSUES

| ID | Description | Blocking | Owner | Status | Created |
|----|-------------|----------|-------|--------|---------|
| ISSUE-001 | Sign trade not working | ~~Yes~~ | BE | ✅ **Resolved** | 2025-12-22 |
| ISSUE-002 | Signal Panel not updating | No | FE | ✅ **Resolved** | 2025-12-22 |

---

## ANNOUNCEMENTS

### [2025-12-22] Backend Audit Complete
Backend codebase fully audited. Key findings:
- Clean Architecture properly implemented
- All 8 core indicators working
- Paper trading functional
- State machine integrated
- EventBus for WebSocket broadcasting

See: agents/backend-engineer/context/progress.md

---

## KNOWLEDGE BASE

### Pattern: Signal Generation Flow
```
Binance WebSocket 
  -> RealtimeService._on_candle_received()
  -> _generate_signals_with_state_check()
  -> Indicators calculate
  -> Signal created
  -> EventBus.publish()
  -> WebSocket broadcast to frontend
```

### Pattern: Clean Architecture Dependencies
```
API -> Application -> Domain <- Infrastructure
(API calls Application, Infrastructure implements Domain interfaces)
```

---

## ENTITY TRACKER

### APIs (Actual from codebase)
| Endpoint | Owner | Status | Consumers |
|----------|-------|--------|-----------|
| /ws/market | BE | Implemented | FE |
| /market/* | BE | Implemented | FE |
| /trades/* | BE | Implemented | FE |
| /settings/* | BE | Implemented | FE |

### Key Services
| Service | Owner | Status | Lines |
|---------|-------|--------|-------|
| RealtimeService | BE | Implemented | 1000+ |
| PaperTradingService | BE | Implemented | 500+ |
| TradingStateMachine | BE | Implemented | 300+ |

### Indicators
| Indicator | Owner | Status | File |
|-----------|-------|--------|------|
| VWAP | BE | Done | vwap_calculator.py |
| Bollinger Bands | BE | Done | bollinger_calculator.py |
| StochRSI | BE | Done | stoch_rsi_calculator.py |
| ADX | BE | Done | adx_calculator.py |
| ATR | BE | Done | atr_calculator.py |

---

## HOW TO USE THIS BOARD

1. CHECK this board at session start
2. UPDATE your row in Active Work when starting/completing tasks
3. LOG decisions that affect other agents
4. CREATE handoff entries when passing work
5. REPORT blockers immediately
6. ADD to Knowledge Base when learning something valuable

---

## UPDATE LOG

| Date | Agent | Change |
|------|-------|--------|
| 2025-12-22 | PM | Created shared board v1.0 |
| 2025-12-22 | PM | Updated with actual codebase status v1.1 |
