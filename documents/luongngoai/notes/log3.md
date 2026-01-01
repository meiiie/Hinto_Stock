Implementation Plan: SFP Detector & Momentum Velocity
Source: 
documents/luongngoai/quytac/chienthuat1.md

Status: 🔍 AWAITING EXPERT REVIEW

Tóm tắt Vấn đề (Chain of Thought Analysis)
Step 1: Tại sao hệ thống hiện tại bị "LAG"?
CHIẾN THUẬT HIỆN TẠI (Trend Pullback):
1. Price pullback to VWAP/BB → ✅ ĐÚNG (mua ở vùng giá trị)
2. StochRSI cross up → ⚠️ CÓ LAG (indicator-based trigger)
3. Volume confirmation → ✅ ĐÚNG
ROOT CAUSE của LAG:

Giá đụng đáy và bắt đầu hồi
StochRSI bắt đầu cắt lên
Signal generated
Bot vào lệnh
THỰC TẾ: Giá đã chạy 0.5-1%
StochRSI là lagging indicator vì:

Cần nhiều candles để tính toán (14 period RSI → 14 period Stoch)
Cần chờ cross xảy ra (thêm 1-2 candles)
Total lag: ~3-5 candles = 3-5 phút trên 1m chart
Step 2: SFP là gì và tại sao nó NHANH HƠN?
# SFP (Swing Failure Pattern) - ICT/SMC Methodology
# BULLISH SFP:
# 1. Price thủng DƯỚI swing low (quét stoploss đám đông)
# 2. Nhưng ĐÓNG CỬA trên swing low (rejection)
# 3. Volume cực lớn (institutional accumulation)
def detect_bullish_sfp(candle, swing_low, volume_ma):
    conditions = {
        "broke_below": candle.low < swing_low,      # Quét thanh khoản
        "closed_above": candle.close > swing_low,   # Rejection mạnh
        "high_volume": candle.volume > 3.0 * volume_ma  # Cá mập hốt hàng
    }
    return all(conditions.values())
SFP nhanh hơn vì:

Phát hiện ngay tại candle xảy ra (không đợi indicator lag)
Đây là price action signal thuần túy
Institutional traders dùng chính pattern này
Step 3: Momentum Velocity giải quyết vấn đề gì?
HIỆN TẠI: Bot nhìn PRICE (giá) → thiếu context về TỐC ĐỘ
VẤN ĐỀ:
- Giá tăng nhanh +1% trong 1 phút → FOMO trap → không nên mua
- Giá giảm CHẬM về VWAP → lực bán yếu → nên mua
GIẢI PHÁP: Thêm Velocity filter
- Rate of change = (close - close[5]) / close[5] * 100 / 5min
- Cho phép mua khi velocity GIẢM (deceleration)
- Block mua khi velocity TĂNG mạnh (FOMO)
Gap Analysis: Hệ thống hiện tại vs Đề xuất
Component	Hiện tại	Đề xuất	Gap
Swing Point Detection	✅ 
swing_point_detector.py
Dùng lại	None
SFP Detector	❌ Chưa có	Cần tạo mới	NEW
Momentum Velocity	❌ Chưa có	Cần tạo mới	NEW
Volume Surge Detection	✅ 
volume_spike_detector.py
Dùng lại	None
Signal Priority	❌ Không có	SFP > StochRSI	MODIFY
Proposed Architecture
Layer 1 Signal Generation
SFP Signal
Passed
FOMO detected
Price Data
Swing Point Detector
Momentum Velocity
Volume Surge
SFP Detector
Velocity Filter
PRIORITY 1: Immediate Entry
VWAP/BB/StochRSI
PRIORITY 2: Pullback Entry
Block Signal
Detailed Implementation
Phase 1: SFP Detector (Priority: HIGH)
File mới: src/infrastructure/indicators/sfp_detector.py

# Pseudo-code for SFP Detector
@dataclass
class SFPResult:
    is_bullish_sfp: bool
    is_bearish_sfp: bool
    swing_price: float
    penetration_percent: float  # Bao nhiêu % thủng qua swing
    rejection_strength: float   # Mức độ rút chân
    volume_surge: float
    confidence: float
class SFPDetector:
    def detect(self, candles, swing_detector, volume_ma) -> SFPResult:
        # 1. Tìm swing low/high gần nhất
        swing_low = swing_detector.find_recent_swing_low(candles[:-1])
        swing_high = swing_detector.find_recent_swing_high(candles[:-1])
        
        current = candles[-1]
        
        # 2. Check Bullish SFP
        if current.low < swing_low.price:  # Thủng đáy
            if current.close > swing_low.price:  # Đóng trên đáy
                # Calculate metrics
                penetration = (swing_low.price - current.low) / swing_low.price * 100
                rejection = (current.close - current.low) / (current.high - current.low)
                volume_surge = current.volume / volume_ma
                
                if volume_surge >= 3.0:  # Institutional activity
                    return SFPResult(
                        is_bullish_sfp=True,
                        swing_price=swing_low.price,
                        penetration_percent=penetration,
                        rejection_strength=rejection,
                        volume_surge=volume_surge,
                        confidence=min(1.0, rejection * volume_surge / 3)
                    )
        
        # 3. Check Bearish SFP (tương tự, ngược lại)
        ...
Integration vào SignalGenerator:

SFP signal có PRIORITY CAO HƠN StochRSI signal
Nếu SFP detected → Entry ngay lập tức (Market Order)
Không cần chờ các confirmation khác
Phase 2: Momentum Velocity Filter (Priority: MEDIUM)
File mới: src/infrastructure/indicators/momentum_velocity.py

@dataclass
class VelocityResult:
    velocity: float  # %/minute
    acceleration: float  # velocity change
    is_decelerating: bool
    is_fomo_spike: bool
    safe_to_buy: bool
class MomentumVelocityCalculator:
    def __init__(self, lookback: int = 5, fomo_threshold: float = 0.2):
        """
        Args:
            lookback: Số candles để đo velocity
            fomo_threshold: Nếu velocity > threshold → FOMO detected
        """
        
    def calculate(self, candles) -> VelocityResult:
        # Rate of change / time
        velocity = (candles[-1].close - candles[-lookback].close) / candles[-lookback].close * 100 / lookback
        
        # Acceleration (2nd derivative)
        prev_velocity = ... # velocity của lookback trước đó
        acceleration = velocity - prev_velocity
        
        return VelocityResult(
            velocity=velocity,
            acceleration=acceleration,
            is_decelerating=acceleration < 0,
            is_fomo_spike=velocity > fomo_threshold,
            safe_to_buy=velocity < fomo_threshold and (is_decelerating or velocity < 0)
        )
Integration:

Áp dụng cho TẤT CẢ signals (kể cả SFP)
Block signal nếu is_fomo_spike = True
Bonus confidence nếu is_decelerating = True
Phase 3: Signal Priority System (Priority: LOW)
Modify: 
src/application/signals/signal_generator.py

class SignalPriority(Enum):
    SFP = 1      # Highest - vào lệnh ngay
    PULLBACK = 2  # Normal - StochRSI trigger
    BREAKOUT = 3  # Lowest - cần nhiều confirmation
def generate_signal(self, candles, symbol):
    # Check SFP first (PRIORITY 1)
    sfp_result = self.sfp_detector.detect(candles, ...)
    if sfp_result.is_bullish_sfp and sfp_result.confidence > 0.7:
        velocity = self.velocity_calculator.calculate(candles)
        if not velocity.is_fomo_spike:
            return TradingSignal(
                signal_type=SignalType.BUY,
                priority=SignalPriority.SFP,
                entry_type="MARKET",  # Immediate entry
                confidence=sfp_result.confidence
            )
    
    # Otherwise, check normal Pullback (PRIORITY 2)
    # ... existing StochRSI logic ...
Expected Impact (from Expert Analysis)
Metric	Before	After SFP+Velocity
Entry Timing	StochRSI lag 3-5 candles	SFP: 0 lag, immediate
FOMO Avoidance	None	Velocity filter blocks
Signal Quality	Good	Higher conviction
Win Rate	65-70%	75-80% (est.)
Verification Plan
Automated Tests
Unit tests cho SFP detection với historical data
Backtest so sánh Win Rate trước/sau
Integration test với SignalGenerator
Manual Verification
Paper trade 48-72 giờ
So sánh số lượng SFP signals vs StochRSI signals
Analyze exit reasons (STOP_LOSS vs TAKE_PROFIT ratio)
Risk Assessment
Risk	Mitigation
SFP false positive	Volume surge threshold (3x)
Over-optimization	Backtest on multiple periods
Velocity too strict	Tunable threshold in config
Files to Create/Modify
NEW Files:
src/infrastructure/indicators/sfp_detector.py
src/infrastructure/indicators/momentum_velocity.py
src/domain/interfaces/i_sfp_detector.py
src/domain/interfaces/i_momentum_velocity.py
MODIFY Files:
src/application/signals/signal_generator.py
 - Add SFP priority
src/infrastructure/di_container.py
 - DI for new detectors
src/config.py
 - SFP and Velocity thresholds
IMPORTANT

Kế hoạch này cần chuyên gia review trước khi implement. Các thông số (volume threshold 3x, velocity 0.2%/min) cần được backtest xác nhận.

Analysis by Quant Specialist AI - Dec 31, 2025