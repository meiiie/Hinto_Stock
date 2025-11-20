"""
Demo Enhanced Signals Panel

Shows how enhanced signals with Entry/TP/SL will be displayed.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.signals.signal_generator import TradingSignal, SignalType


def demo_enhanced_buy_signal():
    """Demo enhanced BUY signal with Entry/TP/SL"""
    print("=" * 70)
    print("DEMO: Enhanced BUY Signal with Entry/TP/SL")
    print("=" * 70)
    
    # Create enhanced BUY signal
    signal = TradingSignal(
        signal_type=SignalType.BUY,
        confidence=0.85,  # 85% confidence (HIGH)
        timestamp=datetime.now(),
        price=50000.0,  # Current market price
        indicators={
            'rsi': 25.0,
            'ema_7': 50100.0,
            'ema_25': 49900.0,
            'ema_crossover': 'bullish',
            'volume_spike_intensity': 'strong'
        },
        reasons=[
            'EMA Bullish Crossover (EMA7 > EMA25)',
            'Volume Spike 2.5x average',
            'RSI Oversold (25.0 < 30)'
        ],
        # Enhanced fields
        entry_price=50400.0,  # Entry at swing high + 0.1%
        tp_levels={
            'tp1': 50900.0,  # 60% position, 1.0% gain
            'tp2': 51400.0,  # 30% position, 2.0% gain
            'tp3': 51900.0   # 10% position, 3.0% gain
        },
        stop_loss=49900.0,  # Stop below swing low, 1.0% risk
        position_size=0.0199,  # BTC for 1% max risk
        risk_reward_ratio=2.5  # 1:2.5 R:R
    )
    
    print(f"\n{signal}")
    print(f"\nConfidence Level: {signal.confidence_level.value.upper()}")
    
    print(f"\n📍 ENTRY PRICE: ${signal.entry_price:,.2f}")
    print(f"   Distance from current: {((signal.entry_price - signal.price) / signal.price * 100):+.2f}%")
    
    print(f"\n🎯 TAKE PROFIT LEVELS:")
    print(f"   TP1: ${signal.tp_levels['tp1']:,.2f} (60% position) - +1.0% gain")
    print(f"   TP2: ${signal.tp_levels['tp2']:,.2f} (30% position) - +2.0% gain")
    print(f"   TP3: ${signal.tp_levels['tp3']:,.2f} (10% position) - +3.0% gain")
    
    print(f"\n🛑 STOP LOSS: ${signal.stop_loss:,.2f}")
    risk_pct = abs((signal.stop_loss - signal.entry_price) / signal.entry_price * 100)
    print(f"   Risk: -{risk_pct:.2f}%")
    
    print(f"\n📊 RISK/REWARD RATIO: 1:{signal.risk_reward_ratio:.2f}")
    print(f"   Rating: {'✅ Excellent' if signal.risk_reward_ratio >= 2.0 else '✓ Good'}")
    
    print(f"\n💰 POSITION SIZE: {signal.position_size:.4f} BTC")
    print(f"   (1% max risk on ${signal.entry_price * signal.position_size:,.2f} position)")
    
    print(f"\n💡 CONTRIBUTING INDICATORS:")
    for reason in signal.reasons:
        print(f"   ✓ {reason}")
    
    print("\n" + "=" * 70)
    print("✅ Enhanced signal ready for dashboard display!")
    print("=" * 70)


def demo_enhanced_sell_signal():
    """Demo enhanced SELL signal with Entry/TP/SL"""
    print("\n" + "=" * 70)
    print("DEMO: Enhanced SELL Signal with Entry/TP/SL")
    print("=" * 70)
    
    # Create enhanced SELL signal
    signal = TradingSignal(
        signal_type=SignalType.SELL,
        confidence=0.78,  # 78% confidence (MEDIUM)
        timestamp=datetime.now(),
        price=52000.0,  # Current market price
        indicators={
            'rsi': 82.0,
            'ema_7': 51900.0,
            'ema_25': 52100.0,
            'ema_crossover': 'bearish',
            'volume_spike_intensity': 'moderate'
        },
        reasons=[
            'EMA Bearish Crossover (EMA7 < EMA25)',
            'Volume Spike 1.8x average',
            'RSI Overbought (82.0 > 80)'
        ],
        # Enhanced fields
        entry_price=51600.0,  # Entry at swing low - 0.1%
        tp_levels={
            'tp1': 51100.0,  # 60% position, 1.0% gain
            'tp2': 50600.0,  # 30% position, 2.0% gain
            'tp3': 50100.0   # 10% position, 3.0% gain
        },
        stop_loss=52100.0,  # Stop above swing high, 1.0% risk
        position_size=0.0192,  # BTC for 1% max risk
        risk_reward_ratio=2.0  # 1:2.0 R:R
    )
    
    print(f"\n{signal}")
    print(f"\nConfidence Level: {signal.confidence_level.value.upper()}")
    
    print(f"\n📍 ENTRY PRICE: ${signal.entry_price:,.2f}")
    print(f"   Distance from current: {((signal.entry_price - signal.price) / signal.price * 100):+.2f}%")
    
    print(f"\n🎯 TAKE PROFIT LEVELS:")
    print(f"   TP1: ${signal.tp_levels['tp1']:,.2f} (60% position) - +1.0% gain")
    print(f"   TP2: ${signal.tp_levels['tp2']:,.2f} (30% position) - +2.0% gain")
    print(f"   TP3: ${signal.tp_levels['tp3']:,.2f} (10% position) - +3.0% gain")
    
    print(f"\n🛑 STOP LOSS: ${signal.stop_loss:,.2f}")
    risk_pct = abs((signal.stop_loss - signal.entry_price) / signal.entry_price * 100)
    print(f"   Risk: -{risk_pct:.2f}%")
    
    print(f"\n📊 RISK/REWARD RATIO: 1:{signal.risk_reward_ratio:.2f}")
    print(f"   Rating: {'✅ Excellent' if signal.risk_reward_ratio >= 2.0 else '✓ Good'}")
    
    print(f"\n💰 POSITION SIZE: {signal.position_size:.4f} BTC")
    print(f"   (1% max risk on ${signal.entry_price * signal.position_size:,.2f} position)")
    
    print(f"\n💡 CONTRIBUTING INDICATORS:")
    for reason in signal.reasons:
        print(f"   ✓ {reason}")
    
    print("\n" + "=" * 70)
    print("✅ Enhanced signal ready for dashboard display!")
    print("=" * 70)


def main():
    """Run demos"""
    print("\n" + "=" * 70)
    print("ENHANCED SIGNALS PANEL - DEMO")
    print("Task 7.2: Update signals panel with enhanced data")
    print("=" * 70)
    
    demo_enhanced_buy_signal()
    demo_enhanced_sell_signal()
    
    print("\n" + "=" * 70)
    print("🎉 TASK 7.2 IMPLEMENTATION COMPLETE!")
    print("=" * 70)
    print("\n📋 What was implemented:")
    print("   ✅ Added Entry/TP/SL fields to TradingSignal")
    print("   ✅ Updated signals_panel.py to display Entry/TP/SL")
    print("   ✅ Added TP1/TP2/TP3 with position sizes")
    print("   ✅ Added Risk/Reward ratio display")
    print("   ✅ Added position size suggestion")
    print("   ✅ Added confidence level property")
    print("\n📊 Dashboard will now show:")
    print("   📍 Entry Price with distance from current")
    print("   🎯 TP1/TP2/TP3 with % gains and position sizes")
    print("   🛑 Stop Loss with % risk")
    print("   📊 Risk/Reward ratio with rating")
    print("   💰 Suggested position size")
    print("\n🚀 Next: Integrate SignalEnhancementService to generate these signals!")
    print("=" * 70)


if __name__ == "__main__":
    main()
