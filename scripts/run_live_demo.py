import asyncio
import signal
import sys
import os
import logging
from datetime import datetime
from typing import Optional

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.services.realtime_service import RealtimeService
from src.domain.entities.trading_signal import TradingSignal

# Configure logging to show errors but not clutter stdout too much
logging.basicConfig(level=logging.WARNING)

# ANSI Color Codes for Terminal Output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class LiveDemo:
    def __init__(self):
        self.service = RealtimeService(symbol='btcusdt', interval='1m')
        self.last_print_time = datetime.min # Initialize to min to allow first print
        self.min_candles_required = 50 # Need at least 50 for EMA50/VWAP
        
    async def start(self):
        clear_screen()
        print(f"{Colors.HEADER}🚀 Hinto Stock - Trend Pullback Live Demo{Colors.ENDC}")
        print(f"{Colors.CYAN}Initializing Backend & Connecting to Binance...{Colors.ENDC}")
        
        # Subscribe to signals
        self.service.subscribe_signals(self.on_signal)
        
        # Subscribe to updates (for price/indicator display)
        self.service.subscribe_updates(self.on_update)
        
        await self.service.start()
        
        # Wait for historical data warmup
        print(f"{Colors.YELLOW}⏳ Warming up indicators (Loading historical data)...{Colors.ENDC}")
        
        while True:
            candle_count = len(self.service.get_candles('1m'))
            if candle_count >= self.min_candles_required:
                print(f"{Colors.GREEN}✅ Data Ready! ({candle_count} candles loaded){Colors.ENDC}")
                break
            
            print(f"\rLoading data... {candle_count}/{self.min_candles_required} candles", end="", flush=True)
            await asyncio.sleep(1)
            
        print("\n" + "-" * 70)
        print(f"{Colors.BOLD}LIVE MONITORING STARTED (Updates every 5s){Colors.ENDC}")
        print("-" * 70)
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()

    async def stop(self):
        print(f"\n{Colors.YELLOW}Stopping service...{Colors.ENDC}")
        await self.service.stop()
        print(f"{Colors.RED}🛑 Service Stopped.{Colors.ENDC}")

    def on_signal(self, signal: TradingSignal):
        """Callback when a trading signal is generated"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if signal.signal_type.value == 'buy':
            color = Colors.GREEN
            icon = "🟢"
        elif signal.signal_type.value == 'sell':
            color = Colors.RED
            icon = "🔴"
        else:
            color = Colors.YELLOW
            icon = "⚪"
            
        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{icon} {color}SIGNAL GENERATED at {timestamp}: {signal.signal_type.value.upper()}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"Price:      ${signal.price:,.2f}")
        print(f"Confidence: {signal.confidence * 100:.1f}%")
        
        if signal.entry_price:
            print(f"Entry:      ${signal.entry_price:,.2f} (Limit)")
        if signal.stop_loss:
            print(f"Stop Loss:  ${signal.stop_loss:,.2f}")
        if signal.tp_levels:
            try:
                tp_str = ', '.join([f'${float(tp):,.2f}' for tp in signal.tp_levels])
                print(f"Take Profit: {tp_str}")
            except Exception:
                print(f"Take Profit: {signal.tp_levels}")
            
        print(f"\nReasons:")
        for reason in signal.reasons:
            print(f"  - {reason}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

    def on_update(self):
        """Callback when data is updated (every candle/tick)"""
        now = datetime.now()
        
        # Rate limit printing to avoid console spam (every 5 seconds)
        # Use total_seconds() to ensure we don't print multiple times in the same second if called rapidly
        if (now - self.last_print_time).total_seconds() < 5.0:
            return
            
        self.last_print_time = now
        
        latest_candle = self.service.get_latest_data('1m')
        if not latest_candle:
            return
            
        timestamp = now.strftime("%H:%M:%S")
        close = latest_candle.close
        
        # Get latest indicators
        indicators = self.service.get_latest_indicators('1m')
        
        # Default values if not ready
        vwap = indicators.get('vwap', 0)
        rsi = indicators.get('rsi', 0)
        stoch_k = indicators.get('stoch_k', 0)
        stoch_d = indicators.get('stoch_d', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_upper = indicators.get('bb_upper', 0)
        
        # Determine trend icon
        if vwap > 0:
            trend_icon = "📈" if close > vwap else "📉"
            vwap_str = f"${vwap:,.2f}"
        else:
            trend_icon = "⏳"
            vwap_str = "Calculating..."
            
        # Determine RSI Color
        if rsi < 35:
            rsi_str = f"{Colors.GREEN}{rsi:.1f}{Colors.ENDC}"

async def main():
    demo = LiveDemo()
    
    # Handle Ctrl+C
    loop = asyncio.get_running_loop()
    
    try:
        await demo.start()
    except KeyboardInterrupt:
        pass
    finally:
        await demo.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
