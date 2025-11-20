# Hinto Stock - Cryptocurrency Trading System 📈

**Status:** 🚧 Alpha (Under Active Development)
**Current Strategy:** Trend Pullback (VWAP + Bollinger Bands)

---

## ⚠️ Project Status: Transition Phase

We are currently transitioning from a "Mean Reversion" strategy to a **"Trend Pullback"** strategy.

| Component | Status | Notes |
| :--- | :--- | :--- |
| **Backend Logic** | ✅ Implemented | VWAP, Bollinger Bands, StochRSI, Smart Entry logic is ready. |
| **Signal Generator** | ✅ Implemented | Generates signals based on new strategy. |
| **Tests** | ✅ Passing | Unit tests verified for new signal logic. |
| **Dashboard UI** | ❌ Outdated | Still displays old indicators (EMA, RSI). **Needs Update.** |
| **Backtesting** | ✅ Verified | 30-Day Backtest: **+30% Return**, **77% Win Rate**. |

---

## 🎯 Objective

Build a high-frequency trading system for **BTC/USDT** (15m timeframe) using a **Trend Pullback** strategy.

### Core Strategy
1.  **Trend Filter:** Price > VWAP (Uptrend)
2.  **Setup:** Price pulls back to Lower Bollinger Band or VWAP.
3.  **Trigger:** StochRSI crossover (oversold zone).
4.  **Entry:** "Smart Limit Entry" (placing limit orders below market price).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests (Verify System Health)
```bash
pytest tests/
```

### 3. Run Dashboard (Note: UI is currently outdated)
```bash
streamlit run src/presentation/dashboard/app.py
```

---

## 📂 Project Structure

```
Hinto_Stock/
├── src/
│   ├── application/
│   │   └── signals/         # 🧠 Signal Logic (Updated)
│   ├── infrastructure/
│   │   └── indicators/      # 📊 VWAP, BB, StochRSI Calculators (Updated)
│   └── presentation/
│       └── dashboard/       # 🖥️ UI (Needs Update)
├── tests/                   # 🧪 Unit Tests (Updated)
└── documents/               # 📚 Documentation
    ├── archive/             # Old/Obsolete docs
    └── backtesting/         # Backtest results
```

---

## 📅 Next Steps (Immediate Priority)

1.  **Update Dashboard:** Visualize VWAP, Bollinger Bands, and StochRSI on the charts.
2.  **Live Test:** Deploy the strategy to a paper trading environment.
