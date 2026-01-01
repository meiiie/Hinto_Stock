# Báo Cáo Phân Tích Chiến Thuật
**Date:** 2026-01-01 22:35  
**Status:** Analysis Complete

---

## 1. Tổng Quan Thay Đổi User Đã Thực Hiện

| Thay đổi | Vị trí | Đánh giá |
|----------|--------|----------|
| Session Filter (8-22 UTC) | signal_generator.py:140-146 | ⚠️ Cần xem xét |
| Volume threshold 1.8 → 1.2x | signal_generator.py:172 | ⚠️ Có thể quá loose |
| Momentum Surf strategy mới | signal_generator.py:221-274 | ❌ Thiếu config |
| Volume Profile SL integration | signal_generator.py:292-309 | ✅ Tốt |
| is_limit_order field | signal_generator.py:212 | ✅ Tốt |
| Trend Pullback disabled | signal_generator.py:276-278 | ✅ OK |

---

## 2. Vấn Đề Phát Hiện

### ❌ Issue 1: StrategyRegistry Thiếu Config cho Momentum Surf

```python
# signal_generator.py line 158-159
elif config.strategy_name == "momentum_surf":
    return self._strategy_momentum_surf(ctx, config, symbol)

# NHƯNG strategy_registry.py KHÔNG CÓ "momentum_surf" config!
# → Kết quả: Momentum Surf không bao giờ được gọi
```

**Fix cần thiết:**
```python
# Thêm vào strategy_registry.py
MOMENTUM_SURF_CONFIG = StrategyConfig(
    strategy_name="momentum_surf",
    vwap_distance_threshold=0.02,
    sfp_confidence_threshold=0.7,
    stop_loss_buffer=0.025,  # 2.5% cho momentum
    tp_targets=[1.05, 1.10],  # 5%, 10%
    use_dynamic_threshold=False
)

_REGISTRY: Dict[str, StrategyConfig] = {
    "BTCUSDT": BTC_CONFIG,
    "TAOUSDT": MOMENTUM_SURF_CONFIG,
    "SOLUSDT": MOMENTUM_SURF_CONFIG,
}
```

---

### ⚠️ Issue 2: Session Filter Timezone

```python
# signal_generator.py line 143-146
current_hour = candles[-1].timestamp.hour
if not (8 <= current_hour <= 22):
    return None

# VẤN ĐỀ: timestamp.hour dựa trên timezone của datetime
# Nếu server ở Vietnam (UTC+7), cần adjust!
# 8-22 UTC = 15:00 - 05:00 UTC+7 (HN time)
```

**Fix đề xuất:**
```python
# Option 1: Ensure candle timestamp is UTC
# Option 2: Adjust for local timezone
import pytz
utc_hour = candles[-1].timestamp.astimezone(pytz.UTC).hour
if not (8 <= utc_hour <= 22):
    return None
```

---

### ⚠️ Issue 3: Volume Threshold Quá Thấp

```python
# Trước đó: vol_ratio < 1.8  (Strictest - từ gopy1.md)
# Hiện tại: vol_ratio < 1.2  (Too loose?)

# 1.2x = chỉ 20% trên trung bình - có thể không phải Volume Climax
# Đề xuất: 1.5x là balance tốt hơn
```

---

### ✅ Điểm Tốt: Volume Profile SL Integration

```python
# stop_loss_calculator.py line 103-153
def calculate_smart_stop_loss(self, entry_price, direction, volume_profile, atr_value):
    # ĐÃ IMPLEMENT ĐÚNG:
    # - BUY: SL < VAL - 0.5*ATR
    # - SELL: SL > VAH + 0.5*ATR
    # - Safety checks included
```

---

## 3. Đề Xuất Sửa Đổi

### 3.1 Strategy Registry - Thêm Momentum Surf

```python
# strategy_registry.py
# Thêm config cho TAO, SOL, và các altcoin momentum

MOMENTUM_SURF_CONFIG = StrategyConfig(
    strategy_name="momentum_surf",
    vwap_distance_threshold=0.02,
    sfp_confidence_threshold=0.7,
    stop_loss_buffer=0.025,
    tp_targets=[1.05, 1.10],
    use_dynamic_threshold=False
)

_REGISTRY = {
    "BTCUSDT": BTC_CONFIG,
    "TAOUSDT": MOMENTUM_SURF_CONFIG,
    "SOLUSDT": MOMENTUM_SURF_CONFIG,
}
```

### 3.2 Volume Threshold - Adjust

```python
# signal_generator.py line 172
# Đề xuất:
if vol_ratio < 1.5:  # Balance giữa 1.2 (too loose) và 1.8 (too strict)
    return None
```

### 3.3 TradingSignal - Thêm is_limit_order field

Cần verify TradingSignal entity có field này:
```python
# Check domain/entities/trading_signal.py
@dataclass
class TradingSignal:
    # ...
    is_limit_order: bool = False  # ← Cần có field này
```

---

## 4. Tóm Tắt Hành Động

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | Thêm Momentum Surf config vào Registry | 🔴 HIGH | ❌ TODO |
| 2 | Fix timezone cho Session Filter | 🟡 MEDIUM | ❌ TODO |
| 3 | Verify is_limit_order field | 🟡 MEDIUM | ❌ TODO |
| 4 | Xem xét volume threshold 1.5x | 🟢 LOW | Discussion |

---

*Phân tích bởi Quant Specialist AI - 2026-01-01 22:35*
