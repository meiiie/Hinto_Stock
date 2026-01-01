# Hinto Stock Trading Bot - Gemini Context

> **Project:** Desktop Crypto Trading Application
> **Version:** 2.3 (Volume Upgrade)
> **Architecture:** Clean Architecture + Multi-Agent AI System

---

## 🎯 Project Overview

- **Domain:** 24/7 Cryptocurrency short-term futures trading
- **Strategy:** Trend Pullback (VWAP + Bollinger Bands + StochRSI)
- **4-Layer Signal System:**
  - Layer 0: Regime Detection (HMM - filtering bad markets)
  - Layer 1: Real-time Signals (VWAP/BB/StochRSI)
  - Layer 2: Institutional Confirmation (Volume Delta + Liquidity Zones) ← COMPLETED
  - Layer 3: LLM Strategic Planning (future)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, Pandas, TA-Lib, WebSockets |
| Frontend | React 18, TypeScript, TailwindCSS, Tauri |
| Database | SQLite (paper trading), In-memory (real-time) |
| Real-time | Binance WebSocket (Combined Streams) |
| **Quant** | **Volume Profile, Volume Delta, Liquidity Zone Detection** |

---

## 📁 Directory Structure

```
src/                          # Backend source (Clean Architecture)
├── domain/                   # Entities, Interfaces
├── application/              # Use cases, Services
├── infrastructure/           # External integrations
└── api/                      # FastAPI routes

frontend/src/                 # React frontend
├── components/               # UI components
├── hooks/                    # Custom hooks
└── utils/                    # Utilities

documents/                    # Documentation & AI Workspace
├── ai-workspace/             # Multi-Agent AI System
│   ├── agents/               # 6 agents (PM, FE, BE, DB, QA, Quant)
│   ├── shared-context/       # Shared board, decisions
│   └── workflows/            # Feature dev, bug fix
└── luongngoai/               # Human-AI interaction guide
```

---

## 🤖 AI Agent System

When working on this project, follow the ai-workspace patterns:

| Agent | Specialization |
|-------|---------------|
| PM | Coordination, planning |
| FE | UI, React, frontend |
| BE | API, logic, backend |
| DB | Schema, queries |
| QA | Testing, quality |
| **Quant** | **Strategy, indicators, risk** |

**Entry point:** `documents/ai-workspace/README.md`

---

## 📋 Coding Conventions

### Python (Backend)
- Use type hints for all functions
- Follow Clean Architecture layers
- Domain entities in `src/domain/entities/`
- Interfaces in `src/domain/interfaces/`
- Services in `src/application/services/`

### TypeScript (Frontend)
- Functional components with hooks
- Props types defined explicitly
- Use custom hooks for logic separation

### General
- No hardcoded values - use constants/config
- All changes require updating progress.md
- Follow SOTA patterns from top organizations

---

## 🚀 Quick Commands

```bash
# Backend
cd backend && python run_real_backend.py

# Frontend  
cd frontend && npm run dev

# GKG server (for code analysis)
gkg server start
```

---

## 📚 Important Files

- **Signal Generator:** `src/application/signals/signal_generator.py`
- **Trading Service:** `src/application/services/paper_trading_service.py`
- **Indicators:** `src/infrastructure/indicators/`
- **AI Workspace:** `documents/ai-workspace/`
- **Research Rules:** `documents/luongngoai/quytac/quytacnghiencuu.md`

---

## ⚠️ Current Focus

1. **Volume Upgrade Phase** - Volume Delta & Liquidity Zones (✅ Completed)
2. **Signal Optimization** - Tuning Confluence Weights
3. **Frontend Integration** - Visualize Liquidity Zones on Chart

---

*Last Updated: 2025-12-31*
