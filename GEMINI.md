# Hinto Stock Trading Bot - Gemini Context

> **Project:** Desktop Crypto Trading Application  
> **Version:** 3.0 (Shark Tank - Limit Sniper)  
> **Architecture:** Clean Architecture + Institutional-Grade Backtest Engine

---

## 🎯 Project Overview

- **Domain:** 24/7 Cryptocurrency short-term futures trading
- **Strategy:** Limit Sniper (Swing Point Liquidity Capture)
- **Key Features:**
  - Institutional-grade Backtest Engine (Look-ahead bias fixed)
  - Multi-symbol Portfolio Trading ("Shark Tank" mode)
  - Dynamic Slippage & Leverage Management
  - Trailing Stop & Breakeven Automation

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, Pandas, TA-Lib |
| Frontend | React 18, TypeScript, Zustand |
| Database | SQLite (paper trading), In-memory (real-time) |
| Real-time | Binance WebSocket |
| **Backtest** | **Custom SOTA Engine with Intra-bar Simulation** |
| **Data Warehouse** | **Parquet + ZSTD (Smart Local Cache)** |

---

## 📁 Directory Structure

```
backend/
├── src/
│   ├── domain/           # Entities, Interfaces
│   ├── application/      # Use cases, Services
│   │   ├── backtest/     # Backtest Engine ← KEY
│   │   ├── signals/      # Signal Generator
│   │   └── services/     # Business logic
│   └── infrastructure/   # Indicators, APIs
├── data/cache/           # Parquet Data Warehouse
├── run_backtest.py       # Portfolio Backtest CLI
└── tests/                # Unit tests

frontend/src/
├── stores/               # Zustand State Management
│   ├── backtestStore.ts  # Backtest state persistence
│   └── marketStore.ts    # Real-time market data
├── components/
│   ├── backtest/         # BacktestChart (memoized)
│   └── ...
└── App.tsx               # Main Dashboard
```

---

## 🚀 Quick Commands

```bash
# Backtest (Portfolio Mode) - Shark Tank
cd backend
python run_backtest.py --top 10 --days 30 --balance 1000 --leverage 10 --no-cb

# Frontend
cd frontend && npm run dev

# Backend API
python run_real_backend.py

# Cache Stats
curl http://localhost:8000/market/cache/stats
```

---

## 📊 Current Strategy: Limit Sniper

```
Logic:
1. Identify Swing High/Low (last 20 candles)
2. Place Limit Order at swing point (0.1% beyond)
3. Stop Loss: 0.5% (Fixed R:R = 4:1)
4. Take Profit: 2% (TP1 = 60%, Trailing = 40%)

Performance (Dec 2025):
- BNB 30-day: +57.59% ($100 → $152.82)
- Win Rate: 53.85%
- 26 trades
```

---

## 🦈 Shark Tank Mode

Multi-symbol portfolio trading:
- Scans 10+ symbols simultaneously
- **Fresh Top 10** fetched on each backtest run
- Only 1-10 positions open at a time
- Automatic capital allocation (10x leverage)

---

## 📦 Smart Local Data Warehouse (NEW)

```
Feature: Parquet-based caching for historical data
- First run: ~5 min (fetches from Binance)
- Subsequent runs: <1 sec (reads from cache)
- Compression: ZSTD (~500KB per symbol/year)
- API: /market/cache/stats, /market/cache/clear
```

---

## ⚠️ Current Focus (Jan 2026)

| Priority | Task | Status |
|----------|------|--------|
| ✅ | Quant Lab Multi-Symbol UI | Done |
| ✅ | Zustand State Persistence | Done |
| ✅ | Smart Local Data Warehouse | Done |
| 🔴 P0 | HTF EMA200 Trend Filter | 🔜 Pending |
| 🔴 P0 | Circuit Breaker (Cooldown) | 🔜 Pending |
| 🟡 P1 | Harsh Market Testing | 🔜 Next |

---

## 📚 Important Files

| File | Purpose |
|------|---------|
| `backend/run_backtest.py` | Portfolio Backtest CLI |
| `backend/src/infrastructure/data/historical_data_loader.py` | Smart Local Data Warehouse |
| `backend/src/application/backtest/execution_simulator.py` | Trade execution simulation |
| `frontend/src/stores/backtestStore.ts` | Zustand state persistence |
| `frontend/src/pages/Backtest.tsx` | Quant Lab UI |

---

*Last Updated: 2026-01-02 23:10*

