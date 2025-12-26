from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any
import numpy as np

from ..dependencies import get_realtime_service


def _convert_numpy(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(item) for item in obj]
    elif isinstance(obj, (np.bool_, np.bool8)):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


router = APIRouter(
    prefix="/system",
    tags=["system"]
)

@router.get("/status")
async def get_status():
    """
    Health check endpoint to verify system status.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "hinto-trader-backend",
        "version": "0.1.0"
    }


@router.get("/debug/signal-check")
async def debug_signal_check():
    """
    Debug endpoint to check why signals aren't being generated.
    
    Returns detailed analysis of all signal conditions:
    - Current price and indicators
    - Each condition status (met/not met)
    - Reason why no signal is generated
    """
    realtime_service = get_realtime_service()
    
    result: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "symbol": realtime_service.symbol,
        "state_machine": {},
        "data_status": {},
        "indicators": {},
        "buy_conditions": {},
        "sell_conditions": {},
        "hard_filters": {},
        "diagnosis": []
    }
    
    # 1. State Machine Status
    state_machine = realtime_service.state_machine
    result["state_machine"] = {
        "current_state": state_machine.state.name,
        "can_receive_signals": state_machine.can_receive_signals,
        "is_halted": state_machine.is_halted,
        "cooldown_remaining": state_machine.cooldown_remaining
    }
    
    if not state_machine.can_receive_signals:
        result["diagnosis"].append(f"❌ State machine in {state_machine.state.name} - cannot receive signals")
    else:
        result["diagnosis"].append(f"✅ State machine in SCANNING - ready for signals")
    
    # 2. Data Status
    candles_1m = list(realtime_service._candles_1m)
    candles_15m = list(realtime_service._candles_15m)
    candles_1h = list(realtime_service._candles_1h)
    
    result["data_status"] = {
        "candles_1m_count": len(candles_1m),
        "candles_15m_count": len(candles_15m),
        "candles_1h_count": len(candles_1h),
        "min_required": 50,
        "has_enough_data": len(candles_1m) >= 50
    }
    
    if len(candles_1m) < 50:
        result["diagnosis"].append(f"❌ Insufficient 1m candles: {len(candles_1m)}/50")
        return result
    else:
        result["diagnosis"].append(f"✅ Sufficient data: {len(candles_1m)} candles")
    
    # 3. Current Price
    latest_candle = candles_1m[-1] if candles_1m else None
    if not latest_candle:
        result["diagnosis"].append("❌ No candle data available")
        return result
        
    current_price = latest_candle.close
    result["indicators"]["current_price"] = current_price
    result["indicators"]["current_candle"] = {
        "open": latest_candle.open,
        "high": latest_candle.high,
        "low": latest_candle.low,
        "close": latest_candle.close,
        "is_green": latest_candle.close > latest_candle.open,
        "timestamp": latest_candle.timestamp.isoformat()
    }
    
    # 4. Calculate Indicators manually for debug
    try:
        # VWAP
        vwap_result = realtime_service.vwap_calculator.calculate_vwap(candles_1m)
        if vwap_result:
            price_vs_vwap = "above" if current_price > vwap_result.vwap else "below"
            vwap_distance = realtime_service.vwap_calculator.calculate_distance_from_vwap(
                current_price, vwap_result.vwap
            )
            result["indicators"]["vwap"] = {
                "value": vwap_result.vwap,
                "price_vs_vwap": price_vs_vwap,
                "distance_pct": vwap_distance
            }
        else:
            result["indicators"]["vwap"] = {"error": "Failed to calculate VWAP"}
            result["diagnosis"].append("❌ Failed to calculate VWAP")
        
        # Bollinger Bands
        bb_result = realtime_service.bollinger_calculator.calculate_bands(candles_1m, current_price)
        if bb_result:
            is_near_lower = realtime_service.bollinger_calculator.is_near_lower_band(
                current_price, bb_result.lower_band, threshold_pct=0.015
            )
            is_near_upper = realtime_service.bollinger_calculator.is_near_upper_band(
                current_price, bb_result.upper_band, threshold_pct=0.015
            )
            result["indicators"]["bollinger"] = {
                "upper_band": bb_result.upper_band,
                "middle_band": bb_result.middle_band,
                "lower_band": bb_result.lower_band,
                "bandwidth": bb_result.bandwidth,
                "percent_b": bb_result.percent_b,
                "is_near_lower": is_near_lower,
                "is_near_upper": is_near_upper
            }
        else:
            result["indicators"]["bollinger"] = {"error": "Failed to calculate BB"}
            result["diagnosis"].append("❌ Failed to calculate Bollinger Bands")
        
        # StochRSI
        stoch_result = realtime_service.stoch_rsi_calculator.calculate_stoch_rsi(candles_1m)
        if stoch_result:
            result["indicators"]["stoch_rsi"] = {
                "k": stoch_result.k_value,
                "d": stoch_result.d_value,
                "zone": stoch_result.zone.value,
                "is_oversold": stoch_result.is_oversold,
                "is_overbought": stoch_result.is_overbought,
                "k_cross_up": stoch_result.k_cross_up,
                "k_cross_down": stoch_result.k_cross_down
            }
        else:
            result["indicators"]["stoch_rsi"] = {"error": "Failed to calculate StochRSI"}
            result["diagnosis"].append("❌ Failed to calculate StochRSI")
        
        # Volume Spike
        volumes = [c.volume for c in candles_1m]
        volume_spike_result = realtime_service.signal_generator.volume_spike_detector.detect_spike_from_list(
            volumes=volumes,
            ma_period=20
        )
        if volume_spike_result:
            result["indicators"]["volume"] = {
                "is_spike": volume_spike_result.is_spike,
                "intensity": volume_spike_result.intensity.value,
                "ratio": volume_spike_result.ratio,
                "threshold": 1.5
            }
        
        # ADX
        if realtime_service.adx_calculator:
            adx_result = realtime_service.adx_calculator.calculate_adx(candles_1m)
            if adx_result:
                result["indicators"]["adx"] = {
                    "value": adx_result.adx_value,
                    "is_trending": adx_result.is_trending,
                    "threshold": 25
                }
        
        # 5. Check BUY Conditions
        buy_conditions = {
            "conditions_met": 0,
            "min_required": 4,
            "details": {}
        }
        
        if vwap_result:
            is_trend_bullish = current_price > vwap_result.vwap
            buy_conditions["details"]["1_trend"] = {
                "condition": "Price > VWAP",
                "met": is_trend_bullish,
                "current": f"${current_price:.2f}",
                "vwap": f"${vwap_result.vwap:.2f}"
            }
            if is_trend_bullish:
                buy_conditions["conditions_met"] += 1
        
        if bb_result and vwap_result:
            is_near_lower = realtime_service.bollinger_calculator.is_near_lower_band(
                current_price, bb_result.lower_band, threshold_pct=0.015
            )
            is_near_vwap = realtime_service.vwap_calculator.calculate_distance_from_vwap(
                current_price, vwap_result.vwap
            ) < 1.0
            is_setup = is_near_lower or is_near_vwap
            buy_conditions["details"]["2_setup"] = {
                "condition": "Near Lower BB or VWAP",
                "met": is_setup,
                "is_near_lower_bb": is_near_lower,
                "is_near_vwap": is_near_vwap
            }
            if is_setup:
                buy_conditions["conditions_met"] += 1
        
        if stoch_result:
            is_trigger = stoch_result.k_cross_up and stoch_result.k_value < 80
            buy_conditions["details"]["3_trigger"] = {
                "condition": "StochRSI K Cross Up (K < 80)",
                "met": is_trigger,
                "k_cross_up": stoch_result.k_cross_up,
                "k_value": stoch_result.k_value
            }
            if is_trigger:
                buy_conditions["conditions_met"] += 1
        
        is_green = latest_candle.close > latest_candle.open
        buy_conditions["details"]["4_candle"] = {
            "condition": "Green Candle",
            "met": is_green
        }
        if is_green:
            buy_conditions["conditions_met"] += 1
        
        if volume_spike_result:
            buy_conditions["details"]["5_volume"] = {
                "condition": "Volume Spike",
                "met": volume_spike_result.is_spike,
                "ratio": volume_spike_result.ratio
            }
            if volume_spike_result.is_spike:
                buy_conditions["conditions_met"] += 1
        
        buy_conditions["would_signal"] = buy_conditions["conditions_met"] >= buy_conditions["min_required"]
        result["buy_conditions"] = buy_conditions
        
        # 6. Check SELL Conditions  
        sell_conditions = {
            "conditions_met": 0,
            "min_required": 4,
            "details": {}
        }
        
        if vwap_result:
            is_trend_bearish = current_price < vwap_result.vwap
            sell_conditions["details"]["1_trend"] = {
                "condition": "Price < VWAP",
                "met": is_trend_bearish
            }
            if is_trend_bearish:
                sell_conditions["conditions_met"] += 1
        
        if bb_result and vwap_result:
            is_near_upper = realtime_service.bollinger_calculator.is_near_upper_band(
                current_price, bb_result.upper_band, threshold_pct=0.015
            )
            is_setup = is_near_upper or is_near_vwap
            sell_conditions["details"]["2_setup"] = {
                "condition": "Near Upper BB or VWAP",
                "met": is_setup
            }
            if is_setup:
                sell_conditions["conditions_met"] += 1
        
        if stoch_result:
            is_trigger = stoch_result.k_cross_down and stoch_result.k_value > 20
            sell_conditions["details"]["3_trigger"] = {
                "condition": "StochRSI K Cross Down (K > 20)",
                "met": is_trigger,
                "k_cross_down": stoch_result.k_cross_down,
                "k_value": stoch_result.k_value
            }
            if is_trigger:
                sell_conditions["conditions_met"] += 1
        
        is_red = latest_candle.close < latest_candle.open
        sell_conditions["details"]["4_candle"] = {
            "condition": "Red Candle",
            "met": is_red
        }
        if is_red:
            sell_conditions["conditions_met"] += 1
        
        if volume_spike_result:
            sell_conditions["details"]["5_volume"] = {
                "condition": "Volume Spike",
                "met": volume_spike_result.is_spike
            }
            if volume_spike_result.is_spike:
                sell_conditions["conditions_met"] += 1
        
        sell_conditions["would_signal"] = sell_conditions["conditions_met"] >= sell_conditions["min_required"]
        result["sell_conditions"] = sell_conditions
        
        # 7. Hard Filters
        if realtime_service.hard_filters:
            result["hard_filters"]["adx_filter_enabled"] = True
            if adx_result:
                adx_check = realtime_service.hard_filters.check_adx_filter(adx_result.adx_value)
                result["hard_filters"]["adx_passed"] = adx_check.passed
                result["hard_filters"]["adx_reason"] = adx_check.reason
                
                if not adx_check.passed:
                    result["diagnosis"].append(f"❌ ADX Filter: {adx_check.reason}")
        
        # 8. Summary Diagnosis
        if not buy_conditions["would_signal"] and not sell_conditions["would_signal"]:
            buy_missing = buy_conditions["min_required"] - buy_conditions["conditions_met"]
            sell_missing = sell_conditions["min_required"] - sell_conditions["conditions_met"]
            
            result["diagnosis"].append(
                f"📊 BUY: {buy_conditions['conditions_met']}/{buy_conditions['min_required']} conditions (missing {buy_missing})"
            )
            result["diagnosis"].append(
                f"📊 SELL: {sell_conditions['conditions_met']}/{sell_conditions['min_required']} conditions (missing {sell_missing})"
            )
            
            # Most common blockers
            if not buy_conditions["details"].get("3_trigger", {}).get("met", False):
                result["diagnosis"].append("💡 BUY blocked by: No StochRSI K Cross Up")
            if not sell_conditions["details"].get("3_trigger", {}).get("met", False):
                result["diagnosis"].append("💡 SELL blocked by: No StochRSI K Cross Down")
        else:
            if buy_conditions["would_signal"]:
                result["diagnosis"].append("🟢 BUY signal conditions MET!")
            if sell_conditions["would_signal"]:
                result["diagnosis"].append("🔴 SELL signal conditions MET!")
    
    except Exception as e:
        result["diagnosis"].append(f"❌ Error during analysis: {str(e)}")
        result["error"] = str(e)
    
    return _convert_numpy(result)
