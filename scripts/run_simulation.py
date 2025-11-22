import sys
import os
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.application.services.paper_trading_service import PaperTradingService
from src.domain.entities.trading_signal import TradingSignal, SignalType
from scripts.force_reset_db import force_reset_db
import sys
import os
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.application.services.paper_trading_service import PaperTradingService
from src.domain.entities.trading_signal import TradingSignal, SignalType
from scripts.force_reset_db import force_reset_db

# Setup Logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

from src.domain.entities.candle import Candle
from src.application.signals.signal_generator import SignalGenerator
from src.infrastructure.indicators.vwap_calculator import VWAPCalculator
from src.infrastructure.indicators.bollinger_calculator import BollingerCalculator
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from src.application.services.smart_entry_calculator import SmartEntryCalculator

def load_real_data():
    """Load historical data from CSV"""
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'btc_15m.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}. Run scripts/fetch_data.py first.")
    
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def run_simulation():
    print("🚀 STARTING REAL DATA SIMULATION (Production Logic)...")
    
    force_reset_db()
    repo = SQLiteOrderRepository()
    service = PaperTradingService(repo)
    
    # 1. Init Signal Generator & Dependencies
    vwap_calc = VWAPCalculator()
    bb_calc = BollingerCalculator()
    stoch_calc = StochRSICalculator()
    smart_entry_calc = SmartEntryCalculator()
    
    generator = SignalGenerator(
        vwap_calculator=vwap_calc,
        bollinger_calculator=bb_calc,
        stoch_rsi_calculator=stoch_calc,
        smart_entry_calculator=smart_entry_calc,
        strict_mode=True # Enforce Trend Pullback logic
    )
    
    # 2. Load Data
    try:
        df = load_real_data()
        print(f"✅ Loaded {len(df)} candles from Real Data.")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 3. Run Simulation
    balance_history = []
    signals_triggered = 0
    trade_log = []
    
    # Convert to Candle objects
    all_candles = []
    for _, row in df.iterrows():
        all_candles.append(Candle(
            timestamp=row['timestamp'],
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        ))
        
    start_time = time.time()
    
    # Rolling Window Simulation
    # We need at least 50 candles for indicators to warm up
    window_size = 50
    
    for i in range(window_size, len(all_candles)):
        current_slice = all_candles[i-window_size:i+1]
        current_candle = current_slice[-1]
        
        # A. Process Market Data (Price Update)
        service.process_market_data(
            current_candle.close, 
            current_candle.high, 
            current_candle.low
        )
        
        # B. Generate Signal using PRODUCTION LOGIC
        active_positions = service.get_positions()
        pending_orders = repo.get_pending_orders()
        
        if not active_positions and not pending_orders:
            signal = generator.generate_signal(current_slice)
            
            if signal and signal.signal_type != SignalType.NEUTRAL:
                service.on_signal_received(signal)
                signals_triggered += 1
                
                # Log
                direction = "BUY" if signal.signal_type == SignalType.BUY else "SELL"
                reasons = ", ".join(signal.reasons)
                trade_log.append(f"[{current_candle.timestamp}] {direction} | Price={current_candle.close:.0f} | Conf={signal.confidence:.2f} | {reasons}")

    duration = time.time() - start_time
    
    # 4. Generate Report
    final_balance = service.get_wallet_balance()
    pnl = final_balance - 10000
    
    output = []
    output.append("="*60)
    output.append(f"📊 REAL DATA SIMULATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("="*60)
    output.append(f"Strategy: PRODUCTION LOGIC (Trend Pullback)")
    output.append(f"Data Source: Binance BTCUSDT (15m)")
    output.append(f"Candles: {len(df)}")
    output.append("-" * 60)
    output.append(f"Initial Balance: $10,000.00")
    output.append(f"Final Balance:   ${final_balance:,.2f}")
    output.append(f"Total PnL:       ${pnl:,.2f} ({(pnl/10000)*100:.2f}%)")
    output.append(f"Total Signals:   {signals_triggered}")
    output.append("-" * 60)
    output.append("📝 TRADE LOG:")
    output.extend(trade_log)
    output.append("="*60)
    
    report_content = "\n".join(output)
    print(report_content)
    
    # Save
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"simulation_real_prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(reports_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"\n✅ Detailed Report saved to: {filepath}")

if __name__ == "__main__":
    run_simulation()
