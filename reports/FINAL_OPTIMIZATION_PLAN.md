# 🚀 Phase 17: Final Optimization & Simulation Plan

**Date:** November 22, 2025
**Objective:** Validate the "Trend Pullback" strategy on 3 months of historical data and ensure positive PnL before Live Deployment.

---

## 1. Current State Analysis
*   **Strategy:** Trend Pullback (VWAP + BB + StochRSI).
*   **Data:** 3 Months of BTC/USDT 15m data (8640 candles) loaded.
*   **Recent Fixes:**
    *   Implemented Strict R:R filter (Must be > 1.0).
    *   Implemented Volume Climax filter (Avoid extreme volatility).
    *   Implemented ADX Filter (Avoid sideways markets).

## 2. Simulation Configuration
*   **Script:** `scripts/run_simulation.py`
*   **Data Source:** `data/btc_15m.csv`
*   **Initial Balance:** $10,000
*   **Risk Per Trade:** 1% (or fixed sizing for testing).
*   **Fees:** 0.04% (Taker/Maker average).

## 3. Success Criteria (KPIs)
To proceed to Live Trading, the simulation must achieve:
1.  **PnL:** > 0% (Positive Net Profit).
2.  **Win Rate:** > 45% (Given R:R > 1.5).
3.  **Drawdown:** < 15%.
4.  **Trade Count:** > 30 trades / 3 months (Statistical significance).

## 4. Action Items
1.  **Code Cleanup:** Ensure `SignalGenerator` is free of syntax errors and "garbage code".
2.  **Run Simulation:** Execute the backtest script.
3.  **Analyze Results:**
    *   If **Green**: Generate `REPORT_SIMULATION_OPTIMIZED.md`.
    *   If **Red**: Analyze `logs/trading.log` to identify bad entries/exits and adjust parameters (e.g., relax StochRSI trigger or tighten Stop Loss).

## 5. Dashboard Update (Parallel Task)
*   The Streamlit Dashboard needs to be updated to visualize the new indicators (VWAP, BB) instead of the old EMA/RSI setup. This is crucial for "Eye-balling" the strategy performance in real-time.
