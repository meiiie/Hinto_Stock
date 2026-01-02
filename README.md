# Hinto Trader Pro 📈 (Quant Lab Edition)

**Professional Desktop Trading Application & Institutional Quant Lab**

**Version:** 3.1 | **Status:** 💎 SOTA Hardcore Verified  
**Strategy:** Limit Sniper (Swing Point Liquidity Capture)  
**Market:** Multi-Token Portfolio × Shark Tank Mode × Compounding Engine

---

## ✨ Key Features (Jan 2026)

- **🧪 Quant Lab Dashboard** - Deep analytics with Equity Curves, Drawdown charts, and SOTA Design System.
- **🦈 Shark Tank Mode** - Multi-symbol portfolio trading (Max 10) with intelligent signal selection.
- ** nhân bản Lãi Kép (Compounding)** - Automatic position sizing based on real-time equity growth.
- **📊 Institutional Backtest v3.1** - Now with **Liquidation Logic** and **Liquidity Caps ($50k)**.
- **🛡️ Hardcore Risk Management** - Per-symbol Circuit Breakers + Portfolio Drawdown Protection.

### 🏆 Hall of Fame Performance (Vốn $1,000)
| Period | ROI | Result | Win Rate | Strategy Mode |
|--------|-----|--------|----------|---------------|
| **Tháng 10/2025** | **+2,800%** | **$29,626** | 37.2% | Shark Tank (No CB) |
| **Tháng 11/2025** | **+813%** | **$9,136** | 31.7% | Shark Tank (No CB) |
| **Tháng 12/2025** | **+181%** | **$2,812** | 35.0% | Hardcore Reality |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GEMINI.md](GEMINI.md) | AI context file for development |
| [Quant Lab Report](documents/luongngoai/notes/quant_lab_implementation_report_20260102.md) | Technical redesign details |
| [Data Warehouse Plan](documents/luongngoai/notes/implementation_plan_data_warehouse.md) | Parquet caching strategy |
| [Strategy Blueprint](documents/luongngoai/prompt/strategy_shark_tank_v3.md) | The "Money Printer" logic |

---

## ⚡ Quick Start

### 1. Setup Environment
```bash
# Create and activate venv
python -m venv .venv
.\.venv\Scripts\activate

# Install SOTA requirements
pip install -r backend/requirements.txt
```

### 2. Run "Chiến Thần" Backtest (Recommended)
```bash
cd backend
python run_backtest.py --top 10 --days 30 --balance 1000 --leverage 10 --no-cb
```

### 3. Launch Quant Lab UI
```bash
# Terminal 1: Backend API
python run_real_backend.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## 🏗️ Architecture

### Clean Architecture Layers
- **Presentation:** React 18 + Vite (Tailwind-free, THEME-based)
- **Application:** FastAPI + Backtest Engine v3.1
- **Infrastructure:** Parquet Data Warehouse (Pending) + Binance REST/WS

---

## 📊 Trading Strategy: Limit Sniper v3.1

**Core Logic:**
1. **Swing Analysis** - 20-period High/Low detection on **M15**.
2. **Trend Filter** - EMA200 bias verification on **H4**.
3. **Execution** - Limit orders placed at `Swing +/- 0.1%`.
4. **Compounding** - Volume = `Balance * 10` (Targeting exponential growth).
5. **Reality Cap** - Max $50,000 notional per order to ensure fillability.

---

## 🎯 Roadmap 2026

### Phase 1: Quant Lab (COMPLETE ✅)
- [x] Institutional Backtest Engine
- [x] Hardcore Liquidation Logic
- [x] Advanced Design System (THEME)
- [x] Multi-Strategy Support

### Phase 2: Data Warehouse (IN PROGRESS 🏗️)
- [ ] Parquet Local Caching (Smart Sync)
- [ ] 1-Year Backtest Capability
- [ ] Historical Data Export

### Phase 3: Live Operations
- [ ] Paper Trading Service
- [ ] Binance API Execution Connector
- [ ] Telegram Performance Alerts

---

## 📝 License
MIT License - Developed by Hinto Engineering Team.

---

*Last Updated: 2026-01-02 22:00 UTC*