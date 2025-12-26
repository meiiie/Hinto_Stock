# 📋 ORDER BLOCK CONFIRMATION - Technical Specification v1.0

> **Quant Specialist AI → Backend Engineer AI Handoff**  
> Created: 2025-12-23  
> Priority: P1 (After HMM Regime Detector)  
> Expected Impact: +5% win rate, better R:R ratio

---

## 1. EXECUTIVE SUMMARY

### 1.1 Problem Statement

Current Hinto Stock signal entries are based on Bollinger Band levels which may or may not align with **significant price zones**. Entry at random pullback levels leads to lower win rate compared to entries at **institutional interest zones**.

### 1.2 Solution

Add **Order Block (OB) validation** as a confluence layer that confirms entry signals are occurring at zones where **institutional traders** have previously shown interest.

### 1.3 Relationship to HMM Regime Detector

```
SIGNAL STACK HIERARCHY:

Layer 0: HMM Regime Detection (P0) ← WHEN to trade
            ↓ (passes trending regimes only)
Layer 0.5: Order Block Validation (P1) ← WHERE to trade  
            ↓ (adds confluence score)
Layer 1: Signal Generation (Existing) ← HOW to trade
            ↓
Final Signal: Enhanced confidence + better entry levels
```

### 1.4 Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Entry at significant levels | Unknown | 70%+ |
| Win rate improvement | Baseline | +5% |
| Average R:R | ~1.5 | 1.8+ |

---

## 2. SMART MONEY CONCEPTS - KEY DEFINITIONS

### 2.1 What is an Order Block?

An **Order Block (OB)** is the last opposing candle before an impulsive price move. It represents a zone where institutional orders were accumulated.

```
BULLISH ORDER BLOCK:
┌─────────────────────────────────────────────────────────┐
│                                                          │
│              ████  <- Impulse Move UP                   │
│              ████                                        │
│              ████                                        │
│     ▼▼▼▼    ████                                        │
│    [CANDLE] ← Last BEARISH candle before impulse        │
│     ▲▲▲▲         = BULLISH ORDER BLOCK                  │
│    ═════                                                 │
│                                                          │
│   Price returns to this zone → Institutional buying     │
│                                                          │
└─────────────────────────────────────────────────────────┘

BEARISH ORDER BLOCK:
┌─────────────────────────────────────────────────────────┐
│                                                          │
│    [CANDLE] ← Last BULLISH candle before impulse        │
│     ▼▼▼▼         = BEARISH ORDER BLOCK                  │
│              ████                                        │
│              ████                                        │
│              ████  <- Impulse Move DOWN                 │
│                                                          │
│   Price rallies to this zone → Institutional selling    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Order Block Validity Criteria

| Criteria | Description | Required? |
|----------|-------------|-----------|
| **Opposing candle** | Bearish before up-move, Bullish before down-move | ✅ Yes |
| **Impulsive move** | Body > 1.5x average body size | ✅ Yes |
| **Not yet mitigated** | Price hasn't returned and broken through | ✅ Yes |
| **Recent** | Within last 50 candles | ✅ Yes |
| **Volume confirmation** | Above average volume on impulse | ⚠️ Preferred |

### 2.3 Order Block Zone

The OB zone is defined by the **high** and **low** of the opposing candle:

```python
class OrderBlock:
    type: Literal["BULLISH", "BEARISH"]
    high: float    # Top of zone
    low: float     # Bottom of zone
    origin_index: int  # Candle index where OB formed
    mitigated: bool = False  # True when price returns and breaks through
```

---

## 3. ARCHITECTURE

### 3.1 Integration Point

```
┌─────────────────────────────────────────────────────────────────┐
│                     SIGNAL GENERATOR                             │
│                                                                  │
│  def generate_signal(candles):                                  │
│      # Layer 0: Regime check                                    │
│      if regime.is_ranging:                                      │
│          return None                                             │
│                                                                  │
│      # Layer 0.5: Order Block confluence (NEW)                  │
│      ob_result = order_block_detector.check_confluence(         │
│          candles, current_price                                 │
│      )                                                           │
│                                                                  │
│      # Layer 1: Existing signal logic                           │
│      signal = check_buy_or_sell_conditions(...)                 │
│                                                                  │
│      # Enhance signal with OB confluence                        │
│      if signal and ob_result:                                   │
│          signal.confidence += ob_result.confluence_score * 0.1 │
│          signal.indicators['ob_zone'] = ob_result.zone          │
│                                                                  │
│      return signal                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 File Structure

```
src/
├── infrastructure/
│   └── indicators/
│       └── order_block_detector.py     # NEW: OB detection
├── domain/
│   └── value_objects/
│       └── order_block_result.py       # NEW: OB result VO
└── application/
    └── signals/
        └── signal_generator.py         # MODIFY: Add OB confluence
```

---

## 4. DOMAIN MODEL

### 4.1 OrderBlockType Enum

```python
from enum import Enum

class OrderBlockType(Enum):
    BULLISH = "bullish"   # Buy zone (demand)
    BEARISH = "bearish"   # Sell zone (supply)
```

### 4.2 OrderBlock Entity

```python
@dataclass
class OrderBlock:
    """Represents an institutional order block zone."""
    
    ob_type: OrderBlockType
    high: float           # Top of zone
    low: float            # Bottom of zone
    origin_index: int     # Candle index where OB formed
    origin_timestamp: datetime
    impulse_strength: float  # How strong was the impulse move (1.0 = avg)
    volume_ratio: float   # Volume relative to average
    mitigated: bool = False
    
    @property
    def mid_price(self) -> float:
        return (self.high + self.low) / 2
    
    @property
    def zone_size(self) -> float:
        return self.high - self.low
    
    def is_price_in_zone(self, price: float) -> bool:
        """Check if price is within OB zone."""
        return self.low <= price <= self.high
```

### 4.3 OrderBlockResult Value Object

```python
@dataclass(frozen=True)
class OrderBlockResult:
    """Result of order block confluence check."""
    
    # Whether price is at a valid OB zone
    has_confluence: bool
    
    # The nearest valid order block (if any)
    active_ob: Optional[OrderBlock]
    
    # Confluence score (0.0 - 1.0)
    # Higher = stronger confluence
    confluence_score: float
    
    # Distance from current price to OB zone (%)
    distance_percent: float
    
    # All detected OBs for debugging
    all_order_blocks: List[OrderBlock]
    
    # Recommendation
    recommendation: str  # "CONFLUENT", "NEAR_ZONE", "NO_CONFLUENCE"
```

---

## 5. ORDER BLOCK DETECTION ALGORITHM

### 5.1 Detection Logic

```python
def detect_order_blocks(
    candles: List[Candle],
    lookback: int = 50,
    impulse_threshold: float = 1.5,
    min_volume_ratio: float = 1.0
) -> List[OrderBlock]:
    """
    Detect valid order blocks in price history.
    
    Algorithm:
    1. For each candle, check if NEXT candle is impulsive
    2. If impulsive UP and current is RED → Bullish OB
    3. If impulsive DOWN and current is GREEN → Bearish OB
    4. Filter out mitigated OBs
    
    Args:
        candles: Price history
        lookback: How many candles to look back
        impulse_threshold: Min body size multiple for impulse
        min_volume_ratio: Min volume ratio for confirmation
        
    Returns:
        List of valid (unmitigated) OrderBlocks
    """
    order_blocks = []
    
    # Calculate average body size
    bodies = [abs(c.close - c.open) for c in candles[-lookback:]]
    avg_body = np.mean(bodies)
    
    # Calculate average volume
    volumes = [c.volume for c in candles[-lookback:]]
    avg_volume = np.mean(volumes)
    
    # Scan for OBs
    for i in range(len(candles) - lookback, len(candles) - 1):
        current = candles[i]
        next_candle = candles[i + 1]
        
        # Check if next candle is impulsive
        next_body = abs(next_candle.close - next_candle.open)
        is_impulsive = next_body > avg_body * impulse_threshold
        
        if not is_impulsive:
            continue
        
        # Bullish OB: RED candle before UP impulse
        is_bullish_ob = (
            current.close < current.open and  # Current is RED
            next_candle.close > next_candle.open  # Next is GREEN (up move)
        )
        
        # Bearish OB: GREEN candle before DOWN impulse
        is_bearish_ob = (
            current.close > current.open and  # Current is GREEN
            next_candle.close < next_candle.open  # Next is RED (down move)
        )
        
        if is_bullish_ob or is_bearish_ob:
            volume_ratio = current.volume / avg_volume if avg_volume > 0 else 1.0
            
            ob = OrderBlock(
                ob_type=OrderBlockType.BULLISH if is_bullish_ob else OrderBlockType.BEARISH,
                high=current.high,
                low=current.low,
                origin_index=i,
                origin_timestamp=current.timestamp,
                impulse_strength=next_body / avg_body,
                volume_ratio=volume_ratio,
                mitigated=False
            )
            order_blocks.append(ob)
    
    # Filter mitigated OBs
    current_price = candles[-1].close
    valid_obs = []
    
    for ob in order_blocks:
        # Check if OB was mitigated (price broke through zone after formation)
        for candle in candles[ob.origin_index + 2:]:  # Skip impulse candle
            if ob.ob_type == OrderBlockType.BULLISH:
                # Bullish OB mitigated if price closed below low
                if candle.close < ob.low:
                    ob.mitigated = True
                    break
            else:
                # Bearish OB mitigated if price closed above high
                if candle.close > ob.high:
                    ob.mitigated = True
                    break
        
        if not ob.mitigated:
            valid_obs.append(ob)
    
    return valid_obs
```

### 5.2 Confluence Check

```python
def check_confluence(
    candles: List[Candle],
    current_price: float,
    signal_type: SignalType,
    max_distance_percent: float = 0.5  # 0.5% max distance
) -> OrderBlockResult:
    """
    Check if current price has OB confluence.
    
    Args:
        candles: Price history
        current_price: Current market price
        signal_type: BUY or SELL
        max_distance_percent: Max % distance from OB to consider
        
    Returns:
        OrderBlockResult with confluence info
    """
    # Detect all valid OBs
    all_obs = detect_order_blocks(candles)
    
    # Filter by signal type
    if signal_type == SignalType.BUY:
        relevant_obs = [ob for ob in all_obs if ob.ob_type == OrderBlockType.BULLISH]
    else:
        relevant_obs = [ob for ob in all_obs if ob.ob_type == OrderBlockType.BEARISH]
    
    if not relevant_obs:
        return OrderBlockResult(
            has_confluence=False,
            active_ob=None,
            confluence_score=0.0,
            distance_percent=float('inf'),
            all_order_blocks=all_obs,
            recommendation="NO_CONFLUENCE"
        )
    
    # Find nearest OB
    nearest_ob = None
    min_distance = float('inf')
    
    for ob in relevant_obs:
        # Distance to zone
        if current_price < ob.low:
            distance = (ob.low - current_price) / current_price * 100
        elif current_price > ob.high:
            distance = (current_price - ob.high) / current_price * 100
        else:
            distance = 0  # Price is IN the zone
        
        if distance < min_distance:
            min_distance = distance
            nearest_ob = ob
    
    # Calculate confluence score
    if min_distance == 0:
        # Price is IN the zone
        confluence_score = 1.0
        recommendation = "CONFLUENT"
    elif min_distance <= max_distance_percent:
        # Price is near the zone
        confluence_score = 1.0 - (min_distance / max_distance_percent)
        recommendation = "NEAR_ZONE"
    else:
        confluence_score = 0.0
        recommendation = "NO_CONFLUENCE"
    
    # Boost score for stronger OBs
    if nearest_ob:
        # Stronger impulse = higher score
        strength_boost = min(nearest_ob.impulse_strength / 2.0, 1.0) * 0.2
        confluence_score = min(confluence_score + strength_boost, 1.0)
    
    return OrderBlockResult(
        has_confluence=confluence_score > 0.5,
        active_ob=nearest_ob,
        confluence_score=confluence_score,
        distance_percent=min_distance,
        all_order_blocks=all_obs,
        recommendation=recommendation
    )
```

---

## 6. INTEGRATION WITH SIGNALGENERATOR

### 6.1 Dependency Injection

```python
def __init__(
    self,
    # Existing dependencies...
    regime_detector: Optional[IRegimeDetector] = None,
    
    # NEW: Order block detector
    order_block_detector: Optional[IOrderBlockDetector] = None,
    
    # Configuration
    use_ob_confluence: bool = True,  # NEW flag
    ob_confluence_boost: float = 0.1,  # Confidence boost when confluent
):
    self.order_block_detector = order_block_detector
    self.use_ob_confluence = use_ob_confluence
    self.ob_confluence_boost = ob_confluence_boost
```

### 6.2 Signal Enhancement

```python
def generate_signal(self, candles: List[Candle]) -> Optional[TradingSignal]:
    # ... Layer 0: Regime filter ...
    # ... Layer 1: Signal generation ...
    
    if signal:
        # === NEW: Layer 0.5 - Order Block Confluence ===
        if self.use_ob_confluence and self.order_block_detector:
            ob_result = self.order_block_detector.check_confluence(
                candles, signal.price, signal.signal_type
            )
            
            if ob_result.has_confluence:
                # Boost confidence
                signal.confidence += ob_result.confluence_score * self.ob_confluence_boost
                signal.confidence = min(signal.confidence, 1.0)
                
                # Add to indicators
                signal.indicators['ob_confluence'] = True
                signal.indicators['ob_score'] = ob_result.confluence_score
                signal.indicators['ob_zone_high'] = ob_result.active_ob.high
                signal.indicators['ob_zone_low'] = ob_result.active_ob.low
                
                signal.reasons.append(
                    f"OB Confluence: {ob_result.recommendation} "
                    f"(score: {ob_result.confluence_score:.2f})"
                )
            else:
                signal.indicators['ob_confluence'] = False
                signal.indicators['ob_score'] = 0.0
    
    return signal
```

---

## 7. CONFIGURATION

```python
ORDER_BLOCK_CONFIG = {
    # Detection parameters
    "lookback_candles": 50,
    "impulse_threshold": 1.5,  # Body > 1.5x average
    "min_volume_ratio": 1.0,   # Above average volume
    
    # Confluence parameters
    "max_distance_percent": 0.5,  # 0.5% max distance from zone
    "min_confluence_score": 0.5,  # Minimum to consider confluent
    
    # Signal enhancement
    "confidence_boost": 0.1,  # +10% confidence when confluent
    
    # Zone validity
    "max_ob_age_candles": 50,  # OBs older than 50 candles expire
}
```

---

## 8. TESTING REQUIREMENTS

### 8.1 Unit Tests

```python
class TestOrderBlockDetector:
    
    def test_bullish_ob_detection(self):
        """Should detect bullish OB before impulse up move."""
        candles = create_candles_with_bullish_impulse()
        obs = detect_order_blocks(candles)
        
        assert len(obs) >= 1
        assert obs[0].ob_type == OrderBlockType.BULLISH
    
    def test_mitigated_ob_filtered(self):
        """Should filter out mitigated (broken) OBs."""
        candles = create_candles_with_mitigated_ob()
        obs = detect_order_blocks(candles)
        
        # All returned OBs should be unmitigated
        for ob in obs:
            assert not ob.mitigated
    
    def test_confluence_in_zone(self):
        """Should return high confluence score when price in OB zone."""
        candles, ob_zone = create_candles_with_price_in_ob()
        result = check_confluence(candles, ob_zone.mid_price, SignalType.BUY)
        
        assert result.has_confluence
        assert result.confluence_score > 0.9
```

---

## 9. DEPENDENCIES

No additional packages required - uses existing numpy/pandas.

---

## 10. HANDOFF TO BACKEND

### 10.1 Files to Create

| File | Description | Priority |
|------|-------------|----------|
| `order_block_detector.py` | OB detection implementation | P1 |
| `order_block_result.py` | OrderBlock + Result VOs | P1 |

### 10.2 Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `signal_generator.py` | Add OB confluence check | P1 |

### 10.3 Validation Checklist

- [ ] OrderBlock detection identifies valid OBs
- [ ] Mitigated OBs are correctly filtered
- [ ] Confluence check returns correct score
- [ ] SignalGenerator adds OB info to signals
- [ ] Unit tests pass

---

## 11. SCOPE LIMITATIONS (P1)

This spec intentionally **EXCLUDES** for P1:

| Feature | Reason | Future Priority |
|---------|--------|-----------------|
| Multi-timeframe OB | Complexity | P2 |
| Fair Value Gap (FVG) | Separate concept | P2 |
| Liquidity grab detection | Separate concept | P3 |
| ICT Kill Zones | Time-based, different logic | P3 |

---

*This specification is ready for Backend Engineer AI implementation after HMM Regime Detector.*
*Estimated implementation time: 0.5-1 day*
*Created by: Quant Specialist AI*
*Date: 2025-12-23*
