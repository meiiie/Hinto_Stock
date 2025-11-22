import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.run_backtest import run_backtest

if __name__ == "__main__":
    with open("backtest_result.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        print("Running Quick Backtest (3 days)...")
        try:
            run_backtest(
                symbol="BTCUSDT",
                timeframe="15m",
                months=1  # 30 days for better statistical significance
            )
        except Exception as e:
            print(f"Backtest failed: {e}")
        finally:
            sys.stdout = sys.__stdout__
