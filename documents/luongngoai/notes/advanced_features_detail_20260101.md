# Chi Tiết Các Tính Năng Nâng Cao
**Date:** 2026-01-01

---

## 1. Order Block Detection - Binance Có Hỗ Trợ Không?

### ❌ Binance API KHÔNG có tính năng Order Block trực tiếp

**Tuy nhiên:** Binance cung cấp đủ data để TỰ XÂY DỰNG:

| Data từ Binance | Dùng để làm gì |
|-----------------|----------------|
| Historical Klines (OHLCV) | ✅ Detect Order Block từ price action |
| Order Book Depth | 💰 Thấy pending orders (optional) |
| Trade History | Tick data - xác nhận volume |

### Order Block là gì?
```
Order Block = Nến cuối cùng NGƯỢC chiều trước khi giá BREAK STRUCTURE

Ví dụ Bullish OB:
   ↓↓↓ Giá giảm
   🔴 Nến đỏ cuối cùng  ← BULLISH ORDER BLOCK
   ↑↑↑ Giá phá lên mạnh (Break of Structure)
```

### Implementation:
```python
# src/infrastructure/indicators/order_block_detector.py
class OrderBlockDetector:
    def detect(self, candles: List[Candle]) -> Optional[OrderBlock]:
        # 1. Tìm Market Structure Break (MSB)
        msb = self._find_market_structure_break(candles)
        if not msb:
            return None
        
        # 2. Order Block = Nến ngược chiều trước MSB
        for i in range(msb.index - 1, -1, -1):
            candle = candles[i]
            if self._is_opposing_candle(candle, msb.direction):
                return OrderBlock(
                    high=candle.high,
                    low=candle.low,
                    midpoint=(candle.high + candle.low) / 2,
                    type='BULLISH' if msb.direction == 'UP' else 'BEARISH'
                )
        return None
```

**Kết luận:** ✅ Có thể tự build với OHLC data từ Binance, KHÔNG cần API đặc biệt.

---

## 2. Fair Value Gap (FVG) Detection

### FVG là gì?
```
FVG = "Khoảng trống" giữa 3 nến liên tiếp
      Giá di chuyển quá nhanh → không fill hết

Bullish FVG (Imbalance):
   Candle 1: High = 100
   Candle 2: Bật lên mạnh (không quan trọng)
   Candle 3: Low = 105
   
   → GAP từ 100-105 = FVG (thị trường sẽ quay lại fill)
```

### Implementation:
```python
# src/infrastructure/indicators/fvg_detector.py  
class FVGDetector:
    def detect(self, candles: List[Candle]) -> List[FVG]:
        fvgs = []
        for i in range(1, len(candles) - 1):
            prev = candles[i - 1]
            curr = candles[i]  # Middle candle
            next_c = candles[i + 1]
            
            # Bullish FVG: Gap UP
            if next_c.low > prev.high:
                fvgs.append(FVG(
                    upper=next_c.low,
                    lower=prev.high,
                    midpoint=(next_c.low + prev.high) / 2,
                    type='BULLISH'
                ))
            
            # Bearish FVG: Gap DOWN  
            if next_c.high < prev.low:
                fvgs.append(FVG(
                    upper=prev.low,
                    lower=next_c.high,
                    midpoint=(prev.low + next_c.high) / 2,
                    type='BEARISH'
                ))
        
        return fvgs
```

### Cách sử dụng:
```python
# Trong signal generation:
fvgs = self.fvg_detector.detect(candles)

# Entry khi giá quay lại fill FVG
for fvg in fvgs:
    if fvg.type == 'BULLISH' and fvg.lower <= current_price <= fvg.upper:
        # Price đang fill FVG → Buy opportunity
        pass
```

---

## 3. Multi-Timeframe (1H + 15m)

### Tại sao cần MTF?
```
15m only = Nhiều noise, whipsaw
1H trend + 15m entry = Higher probability

Ví dụ SOTA:
1H: Price > VWAP → BULLISH BIAS (chỉ tìm BUY)
15m: Wait for SFP/Pullback → ENTRY
```

### Implementation cho Hinto:
```python
# signal_generator.py - Enhanced
def generate_signal(self, candles_15m, symbol, **kwargs):
    # 1. Lấy HTF data (từ cache hoặc API call riêng)
    candles_1h = self._get_htf_candles(symbol, '1h')
    
    # 2. Determine HTF trend
    htf_trend = self._get_htf_trend(candles_1h)
    
    # 3. Only trade WITH the trend
    if htf_trend == 'NEUTRAL':
        return None  # Không trade khi không có trend rõ
    
    # 4. Look for LTF entry
    ctx = self._prepare_market_context(candles_15m)
    
    if htf_trend == 'BULLISH':
        # Chỉ tìm BUY signals
        return self._check_buy_entry(ctx, symbol)
    else:
        # Chỉ tìm SELL signals
        return self._check_sell_entry(ctx, symbol)

def _get_htf_trend(self, candles_1h) -> str:
    """Xác định trend từ 1H timeframe"""
    if len(candles_1h) < 20:
        return 'NEUTRAL'
    
    # Simple: EMA crossover hoặc Price vs VWAP
    vwap = self.vwap_calculator.calculate_vwap(candles_1h)
    current_price = candles_1h[-1].close
    
    if current_price > vwap.vwap * 1.005:
        return 'BULLISH'
    elif current_price < vwap.vwap * 0.995:
        return 'BEARISH'
    return 'NEUTRAL'
```

### Cần thêm gì:
1. **HTF Data Feed** - Lấy candles 1H song song với 15m
2. **Realtime Service update** - Cache 1H candles
3. **StrategyRegistry** - Config per-symbol HTF preference

---

## 4. Volume Profile Integration vào Signal Flow

### Đã có:
```python
# volume_profile_calculator.py - 436 lines, production-ready
VolumeProfileResult:
  - POC (Point of Control)
  - VAH (Value Area High)
  - VAL (Value Area Low)
  - HVN/LVN detection
```

### Cần thêm vào MarketContext:
```python
# signal_generator.py

def _prepare_market_context(self, candles) -> MarketContext:
    ctx = MarketContext(...)
    
    # ADD: Volume Profile
    if self.volume_profile_calculator:
        ctx.volume_profile = self.volume_profile_calculator.calculate(candles)
    
    return ctx
```

### Cách sử dụng trong signal:
```python
def _strategy_sfp_mean_reversion(self, ctx, config, symbol):
    # ... existing logic ...
    
    # NEW: Confluence boost nếu price trong Value Area
    confidence = ctx.sfp_result.confidence
    
    if ctx.volume_profile:
        if ctx.volume_profile.is_price_in_value_area(ctx.current_price):
            confidence += 0.1  # +10% confidence
            reasons.append("Inside Value Area (Volume Profile)")
        
        if ctx.volume_profile.is_price_at_poc(ctx.current_price, tolerance_pct=0.005):
            confidence += 0.15  # +15% near POC
            reasons.append("Near POC (Institutional Interest)")
```

---

## 5. POC làm Support/Resistance cho SL

### Vấn đề hiện tại:
```python
# SL = Entry ± fixed % (1.5%, 2%, 3.5%)
stop_loss = entry_price * (1 - config.stop_loss_buffer)
# → Có thể đặt SL ngay trong vùng có volume cao → dễ bị hunt
```

### SOTA Solution:
```python
def calculate_smart_stop_loss(
    self, 
    entry_price: float, 
    direction: str,
    volume_profile: VolumeProfileResult,
    atr_value: float
) -> float:
    """
    Đặt SL NGOÀI POC/Value Area để tránh bị stop hunt.
    
    Logic:
    - LONG: SL < VAL (dưới Value Area Low)
    - SHORT: SL > VAH (trên Value Area High)
    """
    if direction == 'BUY':
        # SL dưới VAL
        base_sl = volume_profile.val
        # Buffer thêm 0.5 ATR để an toàn
        return base_sl - (atr_value * 0.5)
    else:
        # SL trên VAH
        base_sl = volume_profile.vah
        return base_sl + (atr_value * 0.5)
```

### Ví dụ:
```
Entry: $88,000 (BUY)
POC: $87,500
VAL: $87,000
ATR: $500

SL cũ: $88,000 * 0.985 = $86,680
SL mới: $87,000 - $250 = $86,750 ← Tốt hơn, nằm NGOÀI Value Area
```

---

## 6. Order Book vs Order Block - Phân Biệt Quan Trọng

### Order BOOK (Sổ Lệnh Real-time):
```
= Danh sách BID/ASK đang chờ trên sàn
= Binance API MIỄN PHÍ (wss://stream.binance.com)
= Max 5000 levels, 1200 req/min

Dùng cho: Scalping (seconds), HFT
KHÔNG phù hợp: Hinto (15m/1H trading)
```

### Order BLOCK (ICT Concept):
```
= Vùng giá nơi institutions ĐÃ đặt lệnh
= Detect từ OHLC (không cần Order Book)
= Perfect cho 15m/1H trading

PHÙ HỢP CHO HINTO ✅
```

### Quyết Định Cuối Cùng:
| Feature | Decision | Reason |
|---------|----------|--------|
| Order Book API | ❌ SKIP | Cho scalping, không phù hợp 15m/1H |
| Order Block | ✅ DO | ICT concept, fits our timeframe |

---

## Tóm Tắt Hành Động (Updated)

| Feature | Binance Support | Effort | Priority | Decision |
|---------|-----------------|--------|----------|----------|
| Volume Profile → MarketContext | ✅ ĐÃ CÓ | 2h | 🔴 P1 | ✅ DO |
| POC-based SL | ✅ ĐÃ CÓ VP | 2h | 🔴 P1 | ✅ DO |
| Multi-Timeframe (1H+15m) | ✅ API có sẵn | 1 ngày | 🔴 P1 | ✅ DO |
| Order Block | ✅ Tự build OHLC | 1-2 ngày | 🟡 P2 | ✅ DO |
| FVG Detection | ✅ Tự build OHLC | 0.5 ngày | 🟡 P2 | ✅ DO |
| Order Book (Bid/Ask) | ✅ FREE nhưng | 2+ ngày | ⚪ P3 | ❌ SKIP |

---

## Bug Cần Fix Ngay

```python
# signal_generator.py line 163-165
is_buy_setup = ctx.sfp_result.sfp_type == SFPType.BULLISH...
# ...
if not (is_buy or is_sell):  # ← BUG: phải là is_buy_setup
```

---

*Chi tiết kỹ thuật bởi Quant Specialist AI - 2026-01-01 14:51*
