# Hinto Stock - AI Algorithmic Trading System 📈

**Status:** 🚀 Phase 17: Final Optimization
**Strategy:** Trend Pullback (VWAP + Bollinger Bands + StochRSI)
**Market:** BTC/USDT Futures (15m)

---

## 📖 Documentation
*   **[Project Architecture & Strategy](documents/PROJECT_ARCHITECTURE.md)**: Detailed explanation of the system design and trading logic.
*   **[Final Optimization Plan](reports/FINAL_OPTIMIZATION_PLAN.md)**: Current tasks and goals for the simulation phase.

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest tests/
```

### 3. Run Simulation (Backtest)
```bash
python scripts/run_simulation.py
```

### 4. Launch Dashboard
```bash
streamlit run src/presentation/dashboard/app.py
```
*Note: Dashboard UI is currently being updated to match the new strategy indicators.*

---

## 🛠️ Project Structure
```
Hinto_Stock/
├── src/
│   ├── application/        # Business Logic (SignalGenerator)
│   ├── domain/             # Entities & Interfaces
│   ├── infrastructure/     # Indicators & Data Adapters
│   └── presentation/       # Dashboard UI
├── scripts/                # Utility Scripts (Data Fetching, Simulation)
├── tests/                  # Unit & Integration Tests
├── documents/              # Documentation
│   └── archive/            # Archived reports
└── reports/                # Simulation & Performance Reports
```

---

## 🎯 Goal
To build a professional-grade, automated trading system that generates consistent profits through strict adherence to a statistical edge, utilizing **Clean Architecture** and **Python**.
