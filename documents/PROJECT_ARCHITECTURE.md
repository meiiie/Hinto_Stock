# 🏗️ Hinto Stock Architecture & Strategy Documentation

**Version:** 2.1 (Final Optimization)
**Date:** November 2025
**Status:** Pre-Production / Simulation Tuning

---

## 1. Project Overview

**Hinto Stock** is an automated algorithmic trading system designed for the **Crypto Futures** market (specifically BTC/USDT). It is built using **Python** and follows the **Clean Architecture** principles to ensure maintainability, testability, and scalability.

### 🎯 Core Objective
To generate consistent profits by trading the **Trend Pullback** strategy on the **15-minute (15m)** timeframe, utilizing strict risk management and "Smart Entry" logic.

### 🔑 Key Features
*   **Architecture:** Clean Architecture (Domain, Application, Infrastructure, Presentation).
*   **Market:** Binance Futures (USDT-M).
*   **Strategy:** Trend Pullback (VWAP + Bollinger Bands + StochRSI).
*   **Risk Management:** Dynamic Position Sizing, ATR/Swing Stop Loss, Multi-level Take Profit.
*   **Interface:** Streamlit Dashboard for real-time monitoring and paper trading.

---

## 2. Trading Strategy: "Trend Pullback" (Layer 1)

The system has pivoted from a "Mean Reversion" approach to a robust **Trend Following** strategy. The core philosophy is: *"Trend is King. Buy the dip in an uptrend, sell the rally in a downtrend."*

### 2.1. Indicators
| Indicator | Parameters | Purpose |
| :--- | :--- | :--- |
| **VWAP** | Intraday | **Trend Filter:** Determines the dominant market direction. |
| **Bollinger Bands** | 20, 2.0 | **Value Area:** Identifies dynamic support/resistance for pullbacks. |
| **StochRSI** | 14, 14, 3, 3 | **Trigger:** Pinpoints the exact moment of momentum reversal. |
| **Volume** | MA 20 | **Confirmation:** Validates the strength of the move. |
| **ADX** | 14 | **Filter:** Ensures sufficient trend strength (ADX > 20). |

### 2.2. Signal Logic

#### 🟢 BUY Signal (Long)
1.  **Trend:** Price > VWAP (Bullish Control).
2.  **Setup:** Price pulls back to **Lower Bollinger Band** OR **VWAP**.
3.  **Trigger:** StochRSI (K) crosses **ABOVE 30** (leaving oversold).
4.  **Confirmation:** Green Candle + Volume Spike (optional but preferred).
5.  **Filters:**
    *   **Strict R:R:** Potential Reward / Risk > 1.0.
    *   **Volume Climax:** Volume < 4x Average (Avoid catching falling knives).
    *   **ADX:** > 20 (Avoid choppy/sideways markets).

#### 🔴 SELL Signal (Short)
1.  **Trend:** Price < VWAP (Bearish Control).
2.  **Setup:** Price rallies to **Upper Bollinger Band** OR **VWAP**.
3.  **Trigger:** StochRSI (K) crosses **BELOW 70** (leaving overbought).
4.  **Confirmation:** Red Candle + Volume Spike.
5.  **Filters:** Same as Buy (Strict R:R, Volume Climax, ADX).

### 2.3. Smart Entry & Execution
*   **No Market Orders:** The system avoids FOMO by calculating a **Limit Entry** price.
*   **Logic:** Place limit order at `Close - (Body * 0.3)` for Buys (trying to get a better price than the signal candle close).
*   **Stop Loss:** Placed at the recent Swing Low or calculated via ATR.
*   **Take Profit:**
    *   **TP1:** Upper Band (for Buy) / Lower Band (for Sell).
    *   **TP2:** Trailing Stop via VWAP.

---

## 3. System Architecture (Clean Architecture)

The codebase is organized into concentric layers, with dependencies pointing inwards.

### 📂 Directory Structure
```
src/
├── domain/                 # 🧠 Enterprise Logic (Entities, Interfaces)
│   ├── entities/           # Candle, TradingSignal, Position
│   └── interfaces/         # Repositories, Service Interfaces
│
├── application/            # ⚙️ Business Logic (Use Cases)
│   ├── signals/            # SignalGenerator (The "Brain")
│   └── services/           # RiskManager, TP/SL Calculators
│
├── infrastructure/         # 🔌 External Details (DB, API, Libs)
│   ├── binance/            # Binance API Clients
│   ├── indicators/         # Technical Indicator Implementations
│   └── repositories/       # SQLite/File Storage
│
└── presentation/           # 🖥️ UI & Entry Points
    └── dashboard/          # Streamlit App
```

### 🧩 Key Components

#### `SignalGenerator` (`src/application/signals/`)
The core engine that ingests `Candle` data and produces `TradingSignal` objects. It orchestrates the various indicator calculators and applies the strategy logic defined above.

#### `Indicator Calculators` (`src/infrastructure/indicators/`)
Independent modules responsible for calculating specific technical values (e.g., `VWAPCalculator`, `BollingerCalculator`).

#### `RiskManager` (`src/application/services/`)
Calculates position size based on account balance and risk percentage. Ensures no single trade risks more than the defined limit (e.g., 1-2% of equity).

---

## 4. Current Status & Roadmap

### ✅ Completed
*   Core Backend Implementation.
*   Transition to Trend Pullback Strategy.
*   Integration of VWAP, BB, StochRSI.
*   Smart Entry & Risk Management Logic.

### 🚧 In Progress (Phase 17)
*   **Final Simulation Tuning:** Running backtests on 3 months of data (8640 candles).
*   **Dashboard Update:** Syncing the UI with the new backend indicators.

### 📅 Next Steps
1.  Verify positive PnL (> 0%) on 3-month simulation.
2.  Deploy to Paper Trading (Live Test).
3.  Go Live (Small Capital).
