# 💼 BUSINESS LOGIC RULES - Hinto Stock

**Last Updated:** 2025-12-22
**Owner:** Backend Engineer

---

## 1. SIGNAL GENERATION RULES

### Layer 1: Trend Pullback

#### BUY/LONG Signal
```python
def is_valid_long_signal(candle, indicators):
    """
    All conditions must be TRUE for valid LONG signal.
    """
    conditions = [
        # 1. Uptrend confirmed
        candle.close > indicators.vwap,
        
        # 2. Pullback to support zone
        (candle.low <= indicators.bb_lower) or 
        (candle.low <= indicators.vwap * 1.002),  # Within 0.2%
        
        # 3. Momentum shift
        indicators.stoch_rsi_k > 20 and
        indicators.stoch_rsi_k > indicators.prev_stoch_rsi_k,  # Crossing up
        
        # 4. Volume confirmation
        candle.volume > prev_red_candle.volume,
    ]
    return all(conditions)
```

#### SELL/SHORT Signal
```python
def is_valid_short_signal(candle, indicators):
    """
    All conditions must be TRUE for valid SHORT signal.
    """
    conditions = [
        # 1. Downtrend confirmed
        candle.close < indicators.vwap,
        
        # 2. Rally to resistance zone
        (candle.high >= indicators.bb_upper) or 
        (candle.high >= indicators.vwap * 0.998),  # Within 0.2%
        
        # 3. Momentum shift
        indicators.stoch_rsi_k < 80 and
        indicators.stoch_rsi_k < indicators.prev_stoch_rsi_k,  # Crossing down
        
        # 4. Volume confirmation
        candle.volume > prev_green_candle.volume,
    ]
    return all(conditions)
```

---

## 2. SMART ENTRY CALCULATION

```python
def calculate_smart_entry(candle, direction):
    """
    Calculate limit order entry price.
    Never use market orders.
    """
    body_size = abs(candle.close - candle.open)
    
    # Pullback ratio based on candle strength
    if body_size > candle.atr:
        pullback_ratio = 0.5  # Strong candle: deeper pullback
    else:
        pullback_ratio = 0.3  # Normal candle
    
    if direction == "LONG":
        entry = candle.close - (body_size * pullback_ratio)
        # Never below the low
        entry = max(entry, candle.low)
    else:  # SHORT
        entry = candle.close + (body_size * pullback_ratio)
        # Never above the high
        entry = min(entry, candle.high)
    
    return round(entry, precision)
```

---

## 3. STOP LOSS RULES

### Primary: Swing-based
```python
def calculate_stop_loss(candle, direction, lookback=5):
    """
    SL based on recent swing points.
    """
    if direction == "LONG":
        # Stop below recent swing low
        swing_low = min(c.low for c in candles[-lookback:])
        stop_loss = swing_low * 0.998  # 0.2% buffer
    else:
        # Stop above recent swing high
        swing_high = max(c.high for c in candles[-lookback:])
        stop_loss = swing_high * 1.002
    
    return stop_loss
```

### Fallback: ATR-based
```python
def calculate_stop_loss_atr(entry, direction, atr, multiplier=1.5):
    """
    Fallback when swing method not suitable.
    """
    if direction == "LONG":
        stop_loss = entry - (atr * multiplier)
    else:
        stop_loss = entry + (atr * multiplier)
    
    return stop_loss
```

### Maximum Stop Distance
```python
MAX_STOP_PERCENT = 0.02  # 2% max

def validate_stop_loss(entry, stop_loss, direction):
    stop_percent = abs(entry - stop_loss) / entry
    
    if stop_percent > MAX_STOP_PERCENT:
        raise RiskTooHighError(
            f"Stop distance {stop_percent:.2%} exceeds max {MAX_STOP_PERCENT:.2%}"
        )
```

---

## 4. TAKE PROFIT RULES

```python
def calculate_take_profits(entry, stop_loss, direction):
    """
    Multi-level take profits.
    Risk/Reward minimum 1:1.5
    """
    risk = abs(entry - stop_loss)
    
    if direction == "LONG":
        tp1 = entry + (risk * 1.0)   # 1:1 - Close 50%
        tp2 = entry + (risk * 1.5)   # 1:1.5 - Close 30%
        tp3 = entry + (risk * 2.0)   # 1:2 - Close remaining
    else:
        tp1 = entry - (risk * 1.0)
        tp2 = entry - (risk * 1.5)
        tp3 = entry - (risk * 2.0)
    
    return {
        "tp1": {"price": tp1, "percent": 50},
        "tp2": {"price": tp2, "percent": 30},
        "tp3": {"price": tp3, "percent": 20},
    }
```

---

## 5. POSITION SIZING

```python
def calculate_position_size(
    account_balance: Decimal,
    risk_percent: Decimal,
    entry: Decimal,
    stop_loss: Decimal,
    leverage: int = 1,
) -> Decimal:
    """
    Calculate position size based on risk.
    
    Args:
        account_balance: Total account balance
        risk_percent: Risk per trade (e.g., 0.01 = 1%)
        entry: Entry price
        stop_loss: Stop loss price
        leverage: Leverage to use
    
    Returns:
        Position size in base asset
    """
    risk_amount = account_balance * risk_percent
    risk_per_unit = abs(entry - stop_loss)
    
    position_value = risk_amount / risk_per_unit
    position_size = position_value / entry
    
    # Adjust for leverage
    required_margin = position_value / leverage
    
    return PositionSize(
        quantity=position_size,
        value=position_value,
        margin=required_margin,
    )
```

---

## 6. RISK LIMITS

```python
# Hard limits - cannot be overridden
RISK_LIMITS = {
    "max_risk_per_trade": Decimal("0.01"),     # 1%
    "max_daily_loss": Decimal("0.05"),         # 5%
    "max_open_positions": 5,
    "max_leverage": 20,
    "max_position_value": Decimal("10000"),    # USDT
}

def check_risk_limits(order, account):
    """
    Check all risk limits before placing order.
    Raises RiskLimitExceeded if any limit breached.
    """
    checks = [
        (
            order.risk_amount <= account.balance * RISK_LIMITS["max_risk_per_trade"],
            "Trade risk exceeds maximum"
        ),
        (
            account.daily_loss < account.balance * RISK_LIMITS["max_daily_loss"],
            "Daily loss limit reached"
        ),
        (
            len(account.open_positions) < RISK_LIMITS["max_open_positions"],
            "Maximum open positions reached"
        ),
        (
            order.leverage <= RISK_LIMITS["max_leverage"],
            "Leverage exceeds maximum"
        ),
    ]
    
    for condition, message in checks:
        if not condition:
            raise RiskLimitExceeded(message)
```

---

## 7. SIGNAL EXPIRY

```python
SIGNAL_TTL_SECONDS = 300  # 5 minutes

def is_signal_valid(signal):
    """
    Signals expire after TTL or when conditions change.
    """
    # Time-based expiry
    age = time.now() - signal.created_at
    if age.total_seconds() > SIGNAL_TTL_SECONDS:
        return False
    
    # Condition-based expiry
    if signal.direction == "LONG":
        if current_price < signal.stop_loss:
            return False  # Price hit stop before entry
    else:
        if current_price > signal.stop_loss:
            return False
    
    return True
```

---

## 8. ORDER FLOW

```python
# Valid order state transitions
ORDER_TRANSITIONS = {
    "PENDING": ["FILLED", "CANCELLED", "EXPIRED"],
    "FILLED": ["PARTIAL_CLOSE", "CLOSED"],
    "PARTIAL_CLOSE": ["CLOSED"],
    "CANCELLED": [],  # Terminal
    "EXPIRED": [],    # Terminal
    "CLOSED": [],     # Terminal
}

def transition_order(order, new_status):
    valid_transitions = ORDER_TRANSITIONS.get(order.status, [])
    if new_status not in valid_transitions:
        raise InvalidTransitionError(
            f"Cannot transition from {order.status} to {new_status}"
        )
    order.status = new_status
```

---

## 9. GAME THEORY ENHANCEMENTS

### Stop Loss Jitter
```python
def apply_jitter(stop_loss, direction):
    """
    Add random noise to avoid stop hunting.
    """
    jitter_range = stop_loss * 0.001  # 0.1%
    jitter = random.uniform(-jitter_range, jitter_range)
    
    # Jitter away from obvious levels
    return stop_loss + jitter
```

### Adaptive Exit
```python
def get_exit_strategy(adx_value):
    """
    Adjust exit based on trend strength.
    """
    if adx_value > 30:  # Strong trend
        return {"mode": "TRAILING", "tight": False}
    elif adx_value > 25:  # Moderate trend
        return {"mode": "TRAILING", "tight": True}
    else:  # Weak/No trend
        return {"mode": "QUICK_TP", "target": "TP1"}
```

---

**Status:** 🟡 Documented - Implementation pending
