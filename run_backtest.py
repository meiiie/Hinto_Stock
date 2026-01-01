"""
Hinto Stock Backtest Runner (Portfolio Edition)

CLI tool to run backtests on multiple pairs with SHARED CAPITAL.
Usage:
  python run_backtest.py --symbols "BTCUSDT,BNBUSDT" --days 60 --balance 100
"""

import asyncio
import argparse
import logging
import csv
from datetime import datetime, timedelta, timezone
import os
import sys
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.infrastructure.di_container import DIContainer
from src.application.backtest.backtest_engine import BacktestEngine
from src.infrastructure.api.binance_rest_client import BinanceRestClient
from src.application.backtest.execution_simulator import ExecutionSimulator

# Setup logging
logging.basicConfig(
    level=logging.WARNING, # Reduce noise
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BacktestRunner")
logger.setLevel(logging.INFO)

def print_table(headers: List[str], rows: List[List[str]]):
    """Simple ASCII table printer."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
            
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    separator = "-+- ".join("-" * w for w in widths)
    
    print(header_row)
    print(separator)
    for row in rows:
        print(" | ".join(str(c).ljust(w) for c, w in zip(row, widths)))

async def main():
    parser = argparse.ArgumentParser(description="Hinto Stock Portfolio Backtest")
    parser.add_argument("--symbol", type=str, help="Single trading pair")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of pairs")
    parser.add_argument("--top", type=int, help="Run on top N volume pairs")
    parser.add_argument("--interval", type=str, default="15m", help="Timeframe")
    parser.add_argument("--days", type=int, help="Days to backtest (if start/end not provided)")
    parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, help="End date YYYY-MM-DD")
    parser.add_argument("--balance", type=float, default=10000.0, help="Initial Shared Balance")
    parser.add_argument("--risk", type=float, default=0.01, help="Risk per trade (e.g. 0.01)")
    parser.add_argument("--leverage", type=float, default=0.0, help="Fixed Leverage (e.g. 5.0). If 0, use risk-based.")
    
    args = parser.parse_args()
    
    # 1. Determine Symbols
    symbols = []
    if args.symbol:
        symbols = [args.symbol.upper()]
    elif args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    elif args.top:
        print(f"🔍 Fetching top {args.top} volume pairs from Binance...")
        client = BinanceRestClient()
        symbols = client.get_top_volume_pairs(limit=args.top)
    else:
        symbols = ["BTCUSDT"]

    print(f"🚀 Starting PORTFOLIO Backtest: {len(symbols)} pairs | {args.days} days | ${args.balance} Shared Capital")
    
    # 2. Initialize System (Shared Simulator - Shark Tank)
    container = DIContainer()
    signal_gen = container.get_signal_generator()
    
    simulator = ExecutionSimulator(
        initial_balance=args.balance,
        risk_per_trade=args.risk,
        fixed_leverage=args.leverage,
        mode="SHARK_TANK",
        max_leverage=max(5.0, args.leverage)
    )
    
    engine = BacktestEngine(
        signal_generator=signal_gen,
        simulator=simulator
    )
    
    # 3. Time Range
    if args.start:
        try:
            start_time = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if args.end:
                end_time = datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            else:
                end_time = datetime.now(timezone.utc)
        except ValueError as e:
            logger.error(f"Invalid date format. Use YYYY-MM-DD: {e}")
            return
    else:
        days = args.days or 7
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
    
    # 4. Run Portfolio
    try:
        result = await engine.run_portfolio(
            symbols=symbols,
            interval=args.interval,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        return

    # 5. Report Generation
    stats = result.get('stats', {})
    trades = result.get('trades', [])
    
    print("\n" + "="*60)
    print("📊 PORTFOLIO PERFORMANCE REPORT")
    print("="*60)
    
    # Portfolio Stats
    print(f"💰 Initial Balance: ${stats.get('initial_balance', 0):.2f}")
    print(f"🏁 Final Balance:   ${stats.get('final_balance', 0):.2f}")
    print(f"📈 Net Return:      {stats.get('net_return_pct', 0):.2f}% (${stats.get('net_return_usd', 0):.2f})")
    print(f"🔢 Total Trades:    {stats.get('total_trades', 0)}")
    print(f"🎯 Win Rate:        {stats.get('win_rate', 0):.2f}%")
    
    # Per-Symbol Breakdown
    print("\n--- Symbol Breakdown ---")
    headers = ["Symbol", "Trades", "PnL ($", "Win Rate"]
    symbol_stats = {}
    for t in trades:
        sym = t['symbol']
        if sym not in symbol_stats:
            symbol_stats[sym] = {'count': 0, 'pnl': 0.0, 'wins': 0}
        
        symbol_stats[sym]['count'] += 1
        symbol_stats[sym]['pnl'] += t['pnl_usd']
        if t['pnl_usd'] > 0:
            symbol_stats[sym]['wins'] += 1
            
    rows = []
    for sym, s in symbol_stats.items():
        wr = (s['wins'] / s['count'] * 100) if s['count'] > 0 else 0
        rows.append([sym, str(s['count']), f"${s['pnl']:.2f}", f"{wr:.1f}%"])
        
    print_table(headers, rows)
    print("="*60 + "\n")

    # 6. Export to CSV
    csv_filename = f"portfolio_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Trade ID", "Symbol", "Side", "Entry Time", "Exit Time", "Entry Price", "Exit Price", "PnL ($)", "PnL (%)", "Reason", "Size", "Notional", "Entry Leverage"])
            
            for t in trades:
                writer.writerow([
                    t['trade_id'],
                    t['symbol'], 
                    t['side'], 
                    t['entry_time'].strftime('%Y-%m-%d %H:%M:%S'), 
                    t['exit_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    f"{t['entry_price']:.4f}", 
                    f"{t['exit_price']:.4f}",
                    f"{t['pnl_usd']:.4f}", 
                    f"{t['pnl_pct']:.2f}%",
                    t['exit_reason'],
                    t['position_size'],
                    t['notional_value'],
                    f"{t['leverage_at_entry']:.2f}x"
                ])
        print(f"💾 Detailed trade log saved to: {csv_filename}")
    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")

if __name__ == "__main__":
    asyncio.run(main())