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
        if (now - self.last_print_time).total_seconds() < 5.0:
            return
            
        self.last_print_time = now
        
        latest_candle = self.service.get_latest_data('1m')
        if not latest_candle:
            return
            
        timestamp = now.strftime("%H:%M:%S")
        
        # Get latest indicators
        indicators = self.service.get_latest_indicators('1m')
        indicators_1h = self.service.get_latest_indicators('1h')
        
        # Format output
        price = f"${latest_candle.close:,.2f}"
        
        # VWAP
        vwap = indicators.get('vwap', 0)
        vwap_str = f"${vwap:,.2f}" if vwap > 0 else "N/A"
        
        # StochRSI
        stoch = indicators.get('stoch_rsi', {})
        stoch_k = stoch.get('k', 0)
        stoch_d = stoch.get('d', 0)
        stoch_str = f"{stoch_k:.1f}/{stoch_d:.1f}"
        
        # StochRSI 1h
        stoch_1h = indicators_1h.get('stoch_rsi', {})
        stoch_k_1h = stoch_1h.get('k', 0)
        stoch_d_1h = stoch_1h.get('d', 0)
        stoch_1h_str = f"{stoch_k_1h:.1f}/{stoch_d_1h:.1f}"
        
        # Color coding for StochRSI
        if stoch_k < 20:
            stoch_str = f"{Colors.GREEN}{stoch_str}{Colors.ENDC}"
        elif stoch_k > 80:
            stoch_str = f"{Colors.RED}{stoch_str}{Colors.ENDC}"
            
        # Signal
        latest_signal = self.service.get_current_signals()
        signal_str = "WAITING"
        if latest_signal:
            color = Colors.GREEN if latest_signal.signal_type.value == 'buy' else Colors.RED
            signal_str = f"{color}{latest_signal.signal_type.value.upper()}{Colors.ENDC}"
            if latest_signal.entry_price:
                signal_str += f" @ ${latest_signal.entry_price:,.2f}"
        
        print(f"{timestamp} | {price} | VWAP: {vwap_str} | Stoch: {stoch_str} | Stoch(1h): {stoch_1h_str} | {signal_str}")

async def main():
    demo = LiveDemo()
    
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
