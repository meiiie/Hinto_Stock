SOTA Backtesting Architecture Research
Date: 2026-01-01
Objective: Build vs Buy Decision for Hinto Stock Backtesting

1. Deep Chain of Thought Analysis
Step 1: Define the Problem
Q: Hinto Stock cần validate chiến lược TRƯỚC KHI deploy vào live trading
   → Cần hệ thống backtest để đo:
   - Win Rate, Profit Factor, Sharpe Ratio
   - Drawdown, Recovery Factor
   - Strategy vs Buy-and-Hold comparison
Step 2: Trace the Logic Flow
CURRENT SYSTEM:
SignalGenerator → TradingSignal → PaperTradingService → Position
BACKTEST REQUIREMENT:
Historical Data → SignalGenerator → Simulated Trades → Performance Metrics
                                    ↓
                          [NEED: Execution Simulator]
Step 3: Root Question
"Liệu Freqtrade/VectorBT có thể sử dụng Hinto's SignalGenerator hay cần viết lại strategy theo format của họ?"

2. SOTA Framework Comparison (2025)
Feature	VectorBT	Backtrader	Freqtrade	Custom
Speed	⚡⚡⚡ Fastest	⚡ Slow	⚡⚡ Medium	⚡⚡ Custom
Learning Curve	Steep	Moderate	Moderate	N/A
Live Trading	❌ No	✅ Yes	✅ Yes	✅ Depends
Crypto Focus	✅ Yes	⚠️ Limited	✅✅ Core	✅ Yes
Custom Indicators	✅ Yes	✅ Yes	⚠️ Adaptation	✅✅ Native
Hinto Compatible	⚠️ Rewrite	⚠️ Rewrite	⚠️ Rewrite	✅ Native
3. Critical Analysis: Freqtrade
What Freqtrade Requires
# Freqtrade Strategy Format (THEIR FORMAT)
class MyStrategy(IStrategy):
    def populate_indicators(self, dataframe):
        # Must use their dataframe format
        dataframe['vwap'] = ta.VWAP(dataframe)
        return dataframe
    
    def populate_entry_trend(self, dataframe):
        # Entry conditions in THEIR format
        dataframe.loc[conditions, 'enter_long'] = 1
        return dataframe
Problem with Using Freqtrade
STEP 1: Hinto has SignalGenerator with complex logic
        - MarketContext, SFP, Volume Delta, Liquidity Zones
        
STEP 2: Freqtrade requires translating ALL logic into their format
        - populate_indicators() + populate_entry_trend()
        
STEP 3: 2 codebases to maintain = TECHNICAL DEBT
        - Hinto SignalGenerator (production)
        - Freqtrade Strategy (backtest)
        - Changes in one → must sync to other
        
VERDICT: ❌ NOT RECOMMENDED for Hinto's advanced architecture
4. SOTA Recommendation: Hybrid Approach
Architecture: Custom Backtest Engine + Hinto's Core Logic
┌─────────────────────────────────────────────────────┐
│                 BACKTEST ENGINE                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Historical     ┌──────────────────┐   Simulated   │
│     Data    ──▶  │ HINTO SIGNAL     │ ──▶ Trades    │
│   (Binance)      │ GENERATOR        │    (Virtual)  │
│                  │ (SAME AS PROD)   │               │
│                  └──────────────────┘               │
│                           │                         │
│                           ▼                         │
│              ┌──────────────────────┐               │
│              │ EXECUTION SIMULATOR  │               │
│              │ - Slippage           │               │
│              │ - Commission         │               │
│              │ - Partial Fills      │               │
│              └──────────────────────┘               │
│                           │                         │
│                           ▼                         │
│                 PERFORMANCE METRICS                 │
│          (VectorBT for visualization)               │
│                                                     │
└─────────────────────────────────────────────────────┘
Key Principle: SAME CODE FOR BACKTEST AND PRODUCTION
5. Implementation Plan
Phase 1: Data Layer (Priority)
# src/infrastructure/data/historical_data_loader.py
class HistoricalDataLoader:
    """Load historical klines from Binance API or CSV"""
    
    async def load(self, symbol: str, interval: str, 
                   start: datetime, end: datetime) -> List[Candle]:
        # Returns List[Candle] - SAME format as live
        pass
Phase 2: Backtest Runner
# src/application/backtest/backtest_runner.py
class BacktestRunner:
    """
    SOTA: Event-driven backtest using PRODUCTION SignalGenerator
    """
    
    def __init__(self, signal_generator: SignalGenerator):
        # USE THE SAME SignalGenerator AS PRODUCTION
        self.signal_generator = signal_generator
        self.execution_simulator = ExecutionSimulator()
    
    def run(self, candles: List[Candle]) -> BacktestResult:
        positions = []
        for i, candle in enumerate(candles):
            # Feed candles progressively (no look-ahead bias)
            window = candles[max(0, i-200):i+1]
            
            # Call REAL SignalGenerator
            signal = self.signal_generator.generate_signal(window)
            
            if signal:
                trade = self.execution_simulator.execute(signal, candle)
                positions.append(trade)
        
        return BacktestResult(positions)
Phase 3: Execution Simulator
class ExecutionSimulator:
    """Simulates realistic trade execution"""
    
    def __init__(self, slippage_pct: float = 0.05,
                 commission_pct: float = 0.04):
        self.slippage = slippage_pct / 100
        self.commission = commission_pct / 100
    
    def execute(self, signal: TradingSignal, 
                current_candle: Candle) -> SimulatedTrade:
        # Apply slippage
        fill_price = signal.entry_price * (1 + self.slippage)
        # Apply commission
        net_cost = fill_price * (1 + self.commission)
        return SimulatedTrade(...)
Phase 4: Performance Metrics (Use VectorBT)
# VectorBT for metrics calculation ONLY (not strategy)
import vectorbt as vbt
# Convert our trades to VectorBT format for visualization
portfolio = vbt.Portfolio.from_signals(
    close=price_series,
    entries=entry_signals,
    exits=exit_signals,
    freq='1T'
)
portfolio.stats()  # Sharpe, Sortino, Max Drawdown, etc.
6. What to Learn from Freqtrade
Feature	Worth Adopting	Implementation
Hyperopt	✅ Yes	Grid/Random search for parameters
Data download	✅ Yes	Use freqtrade download-data
Report format	✅ Yes	Similar metrics display
Strategy format	❌ No	Keep Hinto's architecture
Bot integration	❌ No	Already have paper trading
7. Final Verdict
✅ RECOMMENDED: Build Custom + Use VectorBT for Metrics
Rationale:

Single Source of Truth: SignalGenerator used in BOTH backtest and production
No Logic Duplication: Avoid maintaining 2 codebases
Full Control: Custom slippage, market impact, liquidity modeling
VectorBT for Speed: Use VectorBT for metrics calculation, not strategy
SOTA Aligned: Matches institutional quant desk patterns
❌ NOT RECOMMENDED: Port to Freqtrade
Reasons:

Strategy format incompatible with Hinto's advanced architecture
MarketContext, SFP, Volume Delta would need complete rewrite
Maintenance nightmare: changes in 2 places
Loss of Clean Architecture benefits
8. Estimated Effort
Component	Effort	Priority
HistoricalDataLoader	2-3 days	P0
BacktestRunner	3-4 days	P0
ExecutionSimulator	2 days	P1
VectorBT Integration	1 day	P2
Report Generator	2 days	P2
Total: ~10-12 days for MVP backtesting system

9. 🎯 Open-Source Projects Worth Studying
Tier 1: Production-Grade Architecture (Highly Recommended)
1. Nautilus Trader ⭐⭐⭐ (BEST)
GitHub: https://github.com/nautechsystems/nautilus_trader

Aspect	Detail
Stars	2.5k+
Architecture	DDD + Event-Driven + Ports & Adapters
Performance	Rust core + Python interface
Key Insight	SAME CODE for backtest and live
What to Learn:

Domain-Driven Design cho trading entities
MessageBus pattern (loose coupling)
Event-driven backtesting engine
Portfolio-level position management
Folders to Study:

nautilus_trader/
├── core/           # Rust performance core
├── model/          # Domain entities (Order, Position, Instrument)
├── backtest/       # Backtest engine
├── execution/      # Execution simulation
└── adapters/       # Exchange adapters (Binance, etc.)
2. VectorBT Pro ⭐⭐⭐
Website: https://vectorbt.pro

Aspect	Detail
Performance	Fastest (vectorized NumPy/Numba)
Specialty	Mass parameter optimization
Use Case	Ideal for Hinto's metrics calculation
What to Learn:

Vectorized portfolio simulation
Sharpe/Sortino/Calmar calculation
Drawdown analysis
Walk-forward optimization
3. Freqtrade ⭐⭐
GitHub: https://github.com/freqtrade/freqtrade

Aspect	Detail
Focus	Crypto trading bot
Strength	Hyperopt + FreqAI (ML integration)
What to Learn:

Hyperparameter optimization (Optuna integration)
Data download from exchanges
Report generation format
Configuration management
Tier 2: Supplementary References
Project	Learn What
Backtrader	Event-driven basics, clean docs
Zipline	Portfolio rebalancing
Jesse	Modern Python crypto bot
CCXT	Exchange API abstraction
10. Recommended Study Path for Hinto
STEP 1: Study Nautilus Trader Architecture
        ├── model/ → Domain entities (Order, Position)
        ├── backtest/engine.py → Event loop
        └── execution/emulator.py → Slippage simulation
STEP 2: Study VectorBT Metrics
        ├── Portfolio stats calculation
        └── Visualization with Plotly
STEP 3: Apply to Hinto
        ├── Create BacktestEngine using SAME SignalGenerator
        ├── Add ExecutionSimulator
        └── Integrate VectorBT for reporting
Report by Quant Specialist AI - 2026-01-01