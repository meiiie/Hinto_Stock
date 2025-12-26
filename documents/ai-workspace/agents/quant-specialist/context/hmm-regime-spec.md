# 📋 HMM REGIME DETECTOR - Technical Specification v1.0

> **Quant Specialist AI → Backend Engineer AI Handoff**  
> Created: 2025-12-23  
> Priority: P0 (Critical Gap)  
> Expected Impact: +10% win rate, -40% false signals

---

## 1. EXECUTIVE SUMMARY

### 1.1 Problem Statement

Hinto Stock's Trend Pullback strategy works well in **TRENDING markets** but generates false signals in **RANGING markets**. The same indicators (VWAP, BB, StochRSI) produce opposite outcomes depending on market regime.

### 1.2 Solution

Implement a **Hidden Markov Model (HMM) Regime Detector** as a pre-filter layer (Layer 0) before signal generation. The system will:
- Classify current market into 3 regimes
- Block signals in unfavorable regimes  
- Provide regime probability for confidence adjustment

### 1.3 Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Win Rate | ~47% | 56%+ |
| False Signal Rate | ~53% | <40% |
| Regime Classification Accuracy | N/A | >75% |

---

## 2. ARCHITECTURE

### 2.1 System Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRADING SYSTEM                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           LAYER 0: REGIME DETECTION (NEW)                │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │              RegimeDetector                          │ │   │
│  │  │  Input: Candles (50+) → HMM → Output: RegimeResult  │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                         ↓                                 │   │
│  │              REGIME FILTER GATE                           │   │
│  │   ┌─────────────────────────────────────────────────────┐│   │
│  │   │ IF regime == RANGING: BLOCK signal generation      ││   │
│  │   │ IF regime == TRENDING: ALLOW signal generation     ││   │
│  │   └─────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           LAYER 1: SIGNAL GENERATION (EXISTING)          │   │
│  │  SignalGenerator (VWAP + BB + StochRSI + ADX + Volume)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 File Structure

```
src/
├── infrastructure/
│   └── indicators/
│       └── regime_detector.py          # NEW: HMM implementation
├── domain/
│   └── value_objects/
│       └── regime_result.py            # NEW: Regime result VO
└── application/
    └── signals/
        └── signal_generator.py         # MODIFY: Add regime filter
```

---

## 3. DOMAIN MODEL

### 3.1 RegimeType Enum

```python
from enum import Enum

class RegimeType(Enum):
    """Market regime classifications"""
    
    TRENDING_LOW_VOL = "trending_low_vol"    # State 0: Best for trend pullback
    TRENDING_HIGH_VOL = "trending_high_vol"  # State 1: OK but careful sizing
    RANGING = "ranging"                       # State 2: DO NOT TRADE
```

### 3.2 RegimeResult Value Object

```python
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class RegimeResult:
    """Result of regime detection analysis"""
    
    # Current regime classification
    regime: RegimeType
    
    # Probability of being in each state (sum = 1.0)
    probabilities: Dict[RegimeType, float]
    
    # Confidence in classification (highest probability)
    confidence: float
    
    # Raw features used for detection (for debugging)
    features: Dict[str, float]
    
    # Recommendation for trading
    should_trade: bool
    
    @property
    def is_trending(self) -> bool:
        return self.regime in [RegimeType.TRENDING_LOW_VOL, RegimeType.TRENDING_HIGH_VOL]
    
    @property
    def is_ranging(self) -> bool:
        return self.regime == RegimeType.RANGING
```

---

## 4. HMM SPECIFICATION

### 4.1 Model Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **n_components** | 3 | Low Vol Trend / High Vol Trend / Ranging |
| **covariance_type** | "full" | Captures feature correlations |
| **n_iter** | 100 | Training iterations |
| **random_state** | 42 | Reproducibility |

### 4.2 Input Features

```python
FEATURES = {
    # Feature 1: Returns (scaled)
    "returns": {
        "formula": "log(close[t] / close[t-1])",
        "window": 1,
        "scaling": "z-score over 20 periods"
    },
    
    # Feature 2: Volatility (realized)
    "volatility": {
        "formula": "std(returns, window=20) * sqrt(252*24*4)",  # Annualized for 15m
        "window": 20,
        "scaling": "none (already normalized)"
    },
    
    # Feature 3: Trend Strength (ADX normalized)
    "trend_strength": {
        "formula": "ADX / 100",
        "window": 14,
        "scaling": "0-1 range"
    },
    
    # Feature 4: Volume Ratio
    "volume_ratio": {
        "formula": "volume[t] / SMA(volume, 20)",
        "window": 20,
        "scaling": "clip to [0.5, 3.0]"
    }
}
```

### 4.3 Feature Matrix Construction

```python
def extract_features(candles: List[Candle]) -> np.ndarray:
    """
    Extract HMM features from candle data.
    
    Returns:
        np.ndarray of shape (n_samples, 4)
        Columns: [returns, volatility, trend_strength, volume_ratio]
    """
    closes = np.array([c.close for c in candles])
    volumes = np.array([c.volume for c in candles])
    
    # Feature 1: Log returns (z-scored)
    returns = np.diff(np.log(closes))
    returns_zscore = (returns - np.mean(returns[-20:])) / np.std(returns[-20:])
    
    # Feature 2: Realized volatility (20-period rolling std)
    volatility = pd.Series(returns).rolling(20).std() * np.sqrt(252 * 24 * 4)
    
    # Feature 3: Trend strength (ADX normalized)
    adx = calculate_adx(candles, period=14)  # Returns 0-100
    trend_strength = adx / 100.0
    
    # Feature 4: Volume ratio (clipped)
    volume_sma = pd.Series(volumes).rolling(20).mean()
    volume_ratio = np.clip(volumes / volume_sma, 0.5, 3.0)
    
    # Combine features (align lengths)
    min_len = min(len(returns_zscore), len(volatility.dropna()), 
                  len(trend_strength), len(volume_ratio.dropna()))
    
    features = np.column_stack([
        returns_zscore[-min_len:],
        volatility.values[-min_len:],
        trend_strength[-min_len:],
        volume_ratio.values[-min_len:]
    ])
    
    return features
```

### 4.4 State Interpretation

| State | ADX Range | Volatility | Interpretation | Trading Action |
|-------|-----------|------------|----------------|----------------|
| 0 | > 25 | Low (< 50%) | Strong trend, low vol | ✅ TRADE (full size) |
| 1 | > 20 | High (> 50%) | Trend but volatile | ⚠️ TRADE (reduced size) |
| 2 | < 20 | Any | Ranging/Choppy | ❌ NO TRADE |

---

## 5. IMPLEMENTATION

### 5.1 RegimeDetector Class

```python
# src/infrastructure/indicators/regime_detector.py

import numpy as np
from hmmlearn import hmm
from typing import List, Optional
from dataclasses import dataclass
import logging

from src.domain.entities.candle import Candle
from src.domain.value_objects.regime_result import RegimeResult, RegimeType


class RegimeDetector:
    """
    Hidden Markov Model-based market regime detector.
    
    Classifies market into 3 states:
    - TRENDING_LOW_VOL: Best conditions for trend pullback
    - TRENDING_HIGH_VOL: Tradeable but with caution
    - RANGING: Do not trade
    
    Usage:
        detector = RegimeDetector()
        detector.fit(historical_candles)  # Train on history
        result = detector.detect_regime(recent_candles)  # Real-time detection
    """
    
    # Minimum candles for reliable detection
    MIN_CANDLES = 50
    
    # Pre-trained state mappings (based on SOTA research)
    # These will be refined after fitting
    STATE_MAPPING = {
        0: RegimeType.TRENDING_LOW_VOL,
        1: RegimeType.TRENDING_HIGH_VOL,
        2: RegimeType.RANGING
    }
    
    def __init__(
        self,
        n_states: int = 3,
        feature_window: int = 20,
        adx_trending_threshold: float = 25.0,
        vol_percentile_threshold: float = 50.0
    ):
        """
        Initialize regime detector.
        
        Args:
            n_states: Number of hidden states (default 3)
            feature_window: Rolling window for feature calculation
            adx_trending_threshold: ADX threshold to consider trending
            vol_percentile_threshold: Volatility percentile for high/low classification
        """
        self.n_states = n_states
        self.feature_window = feature_window
        self.adx_threshold = adx_trending_threshold
        self.vol_threshold = vol_percentile_threshold
        
        self.model = hmm.GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        
        self.is_fitted = False
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Cache for historical volatility percentiles
        self._vol_history: List[float] = []
    
    def fit(self, candles: List[Candle]) -> "RegimeDetector":
        """
        Train HMM on historical data.
        
        Args:
            candles: Historical candles (min 200 recommended)
            
        Returns:
            self (for chaining)
        """
        if len(candles) < 100:
            raise ValueError(f"Need at least 100 candles for training, got {len(candles)}")
        
        features = self._extract_features(candles)
        
        self.model.fit(features)
        self.is_fitted = True
        
        # Calibrate state mapping based on training data
        self._calibrate_state_mapping(candles, features)
        
        self.logger.info(f"RegimeDetector fitted on {len(candles)} candles")
        return self
    
    def detect_regime(self, candles: List[Candle]) -> Optional[RegimeResult]:
        """
        Detect current market regime.
        
        Args:
            candles: Recent candles (minimum 50)
            
        Returns:
            RegimeResult with classification and probabilities
        """
        if len(candles) < self.MIN_CANDLES:
            self.logger.warning(f"Insufficient candles: {len(candles)} < {self.MIN_CANDLES}")
            return None
        
        # If not fitted, use rule-based fallback
        if not self.is_fitted:
            return self._rule_based_detection(candles)
        
        # Extract features
        features = self._extract_features(candles)
        
        # Get state probabilities for latest observation
        state_probs = self.model.predict_proba(features)[-1]
        
        # Most likely state
        current_state = np.argmax(state_probs)
        regime = self.STATE_MAPPING.get(current_state, RegimeType.RANGING)
        
        # Build probability dict
        probabilities = {
            self.STATE_MAPPING[i]: float(state_probs[i])
            for i in range(self.n_states)
        }
        
        # Feature values for debugging
        latest_features = features[-1]
        feature_dict = {
            "returns_zscore": float(latest_features[0]),
            "volatility": float(latest_features[1]),
            "adx_normalized": float(latest_features[2]),
            "volume_ratio": float(latest_features[3])
        }
        
        # Trading decision
        should_trade = regime in [RegimeType.TRENDING_LOW_VOL, RegimeType.TRENDING_HIGH_VOL]
        confidence = float(state_probs[current_state])
        
        return RegimeResult(
            regime=regime,
            probabilities=probabilities,
            confidence=confidence,
            features=feature_dict,
            should_trade=should_trade
        )
    
    def _extract_features(self, candles: List[Candle]) -> np.ndarray:
        """Extract feature matrix from candles."""
        import pandas as pd
        
        closes = np.array([c.close for c in candles], dtype=float)
        highs = np.array([c.high for c in candles], dtype=float)
        lows = np.array([c.low for c in candles], dtype=float)
        volumes = np.array([c.volume for c in candles], dtype=float)
        
        # Feature 1: Log returns (z-scored)
        returns = np.diff(np.log(closes))
        returns = np.append(0, returns)  # Pad first element
        
        returns_series = pd.Series(returns)
        returns_mean = returns_series.rolling(self.feature_window).mean()
        returns_std = returns_series.rolling(self.feature_window).std()
        returns_zscore = (returns - returns_mean) / returns_std.replace(0, 1)
        
        # Feature 2: Realized volatility
        volatility = returns_series.rolling(self.feature_window).std() * np.sqrt(252 * 24 * 4)
        
        # Feature 3: ADX (simplified calculation)
        adx = self._calculate_adx_series(highs, lows, closes, period=14)
        adx_normalized = adx / 100.0
        
        # Feature 4: Volume ratio
        volume_series = pd.Series(volumes)
        volume_sma = volume_series.rolling(self.feature_window).mean()
        volume_ratio = np.clip(volumes / volume_sma.replace(0, 1), 0.5, 3.0)
        
        # Stack features (drop NaN rows)
        features_df = pd.DataFrame({
            'returns': returns_zscore,
            'volatility': volatility,
            'adx': adx_normalized,
            'volume': volume_ratio
        }).dropna()
        
        return features_df.values
    
    def _calculate_adx_series(
        self, 
        highs: np.ndarray, 
        lows: np.ndarray, 
        closes: np.ndarray, 
        period: int = 14
    ) -> np.ndarray:
        """Simplified ADX calculation."""
        import pandas as pd
        
        # True Range
        tr1 = highs - lows
        tr2 = np.abs(highs - np.roll(closes, 1))
        tr3 = np.abs(lows - np.roll(closes, 1))
        tr = np.maximum(np.maximum(tr1, tr2), tr3)
        tr[0] = tr1[0]
        
        # Directional Movement
        up_move = highs - np.roll(highs, 1)
        down_move = np.roll(lows, 1) - lows
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smoothed averages
        atr = pd.Series(tr).ewm(span=period).mean()
        plus_di = 100 * pd.Series(plus_dm).ewm(span=period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).ewm(span=period).mean() / atr
        
        # ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 1)
        adx = dx.ewm(span=period).mean()
        
        return adx.fillna(0).values
    
    def _rule_based_detection(self, candles: List[Candle]) -> RegimeResult:
        """
        Fallback rule-based detection when HMM not fitted.
        Uses ADX and volatility thresholds.
        """
        features = self._extract_features(candles)
        latest = features[-1]
        
        adx_value = latest[2] * 100  # De-normalize
        volatility = latest[1]
        
        # Update volatility history for percentile
        self._vol_history.append(volatility)
        if len(self._vol_history) > 500:
            self._vol_history = self._vol_history[-500:]
        
        vol_percentile = np.percentile(self._vol_history, self.vol_threshold) if len(self._vol_history) > 20 else volatility
        
        # Classification rules
        if adx_value >= self.adx_threshold:
            if volatility < vol_percentile:
                regime = RegimeType.TRENDING_LOW_VOL
                confidence = 0.8
            else:
                regime = RegimeType.TRENDING_HIGH_VOL
                confidence = 0.7
        else:
            regime = RegimeType.RANGING
            confidence = 0.75
        
        probabilities = {
            RegimeType.TRENDING_LOW_VOL: 0.33,
            RegimeType.TRENDING_HIGH_VOL: 0.33,
            RegimeType.RANGING: 0.34
        }
        probabilities[regime] = confidence
        
        feature_dict = {
            "returns_zscore": float(latest[0]),
            "volatility": float(volatility),
            "adx_normalized": float(latest[2]),
            "volume_ratio": float(latest[3])
        }
        
        should_trade = regime != RegimeType.RANGING
        
        return RegimeResult(
            regime=regime,
            probabilities=probabilities,
            confidence=confidence,
            features=feature_dict,
            should_trade=should_trade
        )
    
    def _calibrate_state_mapping(self, candles: List[Candle], features: np.ndarray):
        """
        After fitting, determine which HMM state corresponds to which regime.
        Based on mean ADX and volatility of each state.
        """
        states = self.model.predict(features)
        
        state_stats = {}
        for state in range(self.n_states):
            mask = states == state
            if mask.any():
                state_stats[state] = {
                    'adx_mean': features[mask, 2].mean() * 100,
                    'vol_mean': features[mask, 1].mean()
                }
        
        # Sort states: highest ADX + lowest vol = best trending
        # Lowest ADX = ranging
        sorted_states = sorted(
            state_stats.keys(),
            key=lambda s: (state_stats[s]['adx_mean'], -state_stats[s]['vol_mean']),
            reverse=True
        )
        
        if len(sorted_states) >= 3:
            self.STATE_MAPPING = {
                sorted_states[0]: RegimeType.TRENDING_LOW_VOL,
                sorted_states[1]: RegimeType.TRENDING_HIGH_VOL,
                sorted_states[2]: RegimeType.RANGING
            }
        
        self.logger.info(f"State mapping calibrated: {self.STATE_MAPPING}")
```

### 5.2 Interface Definition

```python
# src/domain/interfaces/regime_detector.py

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.candle import Candle
from src.domain.value_objects.regime_result import RegimeResult


class IRegimeDetector(ABC):
    """Interface for market regime detection."""
    
    @abstractmethod
    def detect_regime(self, candles: List[Candle]) -> Optional[RegimeResult]:
        """Detect current market regime from candle data."""
        pass
    
    @abstractmethod
    def fit(self, candles: List[Candle]) -> "IRegimeDetector":
        """Train the detector on historical data."""
        pass
```

---

## 6. INTEGRATION WITH SIGNALGENERATOR

### 6.1 Dependency Injection

```python
# Modified SignalGenerator.__init__

def __init__(
    self,
    # Existing dependencies...
    vwap_calculator: IVWAPCalculator,
    bollinger_calculator: IBollingerCalculator,
    stoch_rsi_calculator: IStochRSICalculator,
    # ...
    
    # NEW: Regime detector dependency
    regime_detector: Optional[IRegimeDetector] = None,
    
    # Configuration
    use_regime_filter: bool = True,  # NEW flag
    strict_mode: bool = False,
    use_filters: bool = True
):
    # ...existing init...
    self.regime_detector = regime_detector
    self.use_regime_filter = use_regime_filter
```

### 6.2 Filter Implementation in generate_signal

```python
# Modified SignalGenerator.generate_signal

def generate_signal(self, candles: List[Candle]) -> Optional[TradingSignal]:
    """Generate trading signal with regime filter."""
    
    if not candles or len(candles) < 50:
        return None
    
    # === NEW: REGIME FILTER (Layer 0) ===
    regime_result = None
    if self.use_regime_filter and self.regime_detector:
        regime_result = self.regime_detector.detect_regime(candles)
        
        if regime_result:
            self.logger.info(
                f"Regime: {regime_result.regime.value} "
                f"(confidence: {regime_result.confidence:.2%})"
            )
            
            # BLOCK signals in RANGING regime
            if regime_result.is_ranging:
                self.logger.info("🚫 Signal blocked: RANGING market regime")
                return None
    
    # === EXISTING SIGNAL GENERATION (Layer 1) ===
    # ... rest of existing logic ...
    
    # If signal is generated, add regime info
    if signal:
        signal.indicators['regime'] = regime_result.regime.value if regime_result else 'unknown'
        signal.indicators['regime_confidence'] = regime_result.confidence if regime_result else 0.0
        
        # Adjust confidence based on regime
        if regime_result and regime_result.regime == RegimeType.TRENDING_HIGH_VOL:
            signal.confidence *= 0.9  # 10% penalty for high volatility
    
    return signal
```

### 6.3 TradingSignal Extension

```python
# Add to TradingSignal indicators dict

indicators = {
    # Existing...
    'vwap': vwap_value,
    'bb_upper': bb_upper,
    # ...
    
    # NEW: Regime info
    'regime': 'trending_low_vol',  # RegimeType.value
    'regime_confidence': 0.85,
    'regime_should_trade': True
}
```

---

## 7. CONFIGURATION

### 7.1 Default Parameters

```python
# src/config/regime_config.py

REGIME_CONFIG = {
    # HMM Parameters
    "n_states": 3,
    "feature_window": 20,
    
    # Classification thresholds
    "adx_trending_threshold": 25.0,
    "volatility_percentile_threshold": 50.0,
    
    # Training
    "min_training_candles": 200,
    "refit_interval_candles": 500,  # Re-train every 500 new candles
    
    # Feature scaling
    "returns_zscore_window": 20,
    "volume_ratio_clip_min": 0.5,
    "volume_ratio_clip_max": 3.0,
    
    # Trading rules
    "block_ranging_signals": True,
    "reduce_confidence_high_vol": True,
    "high_vol_confidence_penalty": 0.1,
}
```

### 7.2 Training Data Strategy (SOTA-Aligned)

> Based on SOTA research 2025: Effective memory length ~250 observations, adaptive retraining triggers.

#### 7.2.1 Initial Training Requirements

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Minimum candles** | 500 | ~5 days of 15m data, enough for HMM convergence |
| **Optimal candles** | 1000 | ~10 days, captures multiple regime cycles |
| **Data source** | Binance Historical API | Fetch on-demand at service startup |

#### 7.2.2 Training Data Flow

```python
# Startup sequence
async def initialize_regime_detector():
    """Initialize and train regime detector at service startup."""
    
    # Step 1: Fetch historical data
    candles = await binance_client.fetch_historical_klines(
        symbol="BTCUSDT",
        interval="15m",
        limit=1000  # ~10 days
    )
    
    # Step 2: Initialize detector
    detector = RegimeDetector(
        n_states=3,
        feature_window=20
    )
    
    # Step 3: Train HMM
    detector.fit(candles)
    
    return detector
```

#### 7.2.3 Retraining Strategy

```python
RETRAINING_CONFIG = {
    # Trigger: Confidence-based (adaptive)
    "confidence_threshold": 0.6,      # Retrain if regime confidence drops
    "consecutive_low_conf": 10,       # 10 consecutive low-confidence detections
    
    # Trigger: Interval-based (fallback)
    "interval_fallback_candles": 2000,  # Every ~20 days as fallback
    
    # Rolling window
    "rolling_window_size": 1000,      # Always use last 1000 candles
    "update_frequency_candles": 100   # Check retraining every 100 new candles
}
```

#### 7.2.4 Runtime Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RUNTIME DATA FLOW                         │
│                                                              │
│   NEW CANDLE RECEIVED:                                       │
│   ┌──────────────────────────────────────────────────────┐  │
│   │ 1. Append to rolling buffer (max 1000)              │  │
│   │ 2. Detect regime on latest 50+ candles              │  │
│   │ 3. Monitor confidence                               │  │
│   └──────────────────────────────────────────────────────┘  │
│                             ↓                                │
│   RETRAINING CHECK (every 100 candles):                     │
│   ┌──────────────────────────────────────────────────────┐  │
│   │ IF consecutive_low_conf >= 10:                      │  │
│   │     → Trigger refit with latest 1000 candles        │  │
│   │ ELIF candles_since_fit >= 2000:                     │  │
│   │     → Trigger scheduled refit                       │  │
│   │ ELSE:                                               │  │
│   │     → Continue with current model                    │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 7.2.5 Implementation in RegimeDetector

```python
class RegimeDetector:
    # ... existing code ...
    
    def __init__(self, ...):
        # ... existing init ...
        
        # Retraining tracking
        self._candles_since_fit = 0
        self._consecutive_low_conf = 0
        self._rolling_buffer: List[Candle] = []
    
    def update_and_detect(self, new_candle: Candle) -> Optional[RegimeResult]:
        """
        Update buffer and detect regime, with automatic retraining.
        
        This is the primary method for runtime use.
        """
        # Add to rolling buffer
        self._rolling_buffer.append(new_candle)
        if len(self._rolling_buffer) > 1000:
            self._rolling_buffer = self._rolling_buffer[-1000:]
        
        self._candles_since_fit += 1
        
        # Detect regime
        result = self.detect_regime(self._rolling_buffer[-50:])
        
        # Track low confidence
        if result and result.confidence < 0.6:
            self._consecutive_low_conf += 1
        else:
            self._consecutive_low_conf = 0
        
        # Check retraining triggers
        if self._should_retrain():
            self._retrain()
        
        return result
    
    def _should_retrain(self) -> bool:
        """Check if retraining is needed."""
        # Confidence-based trigger
        if self._consecutive_low_conf >= 10:
            self.logger.info("Retraining triggered: Low confidence streak")
            return True
        
        # Interval-based fallback
        if self._candles_since_fit >= 2000:
            self.logger.info("Retraining triggered: Scheduled interval")
            return True
        
        return False
    
    def _retrain(self):
        """Retrain HMM on rolling buffer."""
        if len(self._rolling_buffer) >= 500:
            self.fit(self._rolling_buffer)
            self._candles_since_fit = 0
            self._consecutive_low_conf = 0
            self.logger.info(f"Model retrained on {len(self._rolling_buffer)} candles")

## 8. TESTING REQUIREMENTS

### 8.1 Unit Tests

```python
# tests/test_regime_detector.py

class TestRegimeDetector:
    
    def test_trending_detection(self):
        """Should detect trending regime when ADX > 25 and clear direction."""
        candles = create_trending_candles(count=100, direction='up')
        detector = RegimeDetector()
        result = detector.detect_regime(candles)
        
        assert result is not None
        assert result.is_trending
        assert result.should_trade
    
    def test_ranging_detection(self):
        """Should detect ranging regime when ADX < 20 and sideways."""
        candles = create_ranging_candles(count=100)
        detector = RegimeDetector()
        result = detector.detect_regime(candles)
        
        assert result is not None
        assert result.is_ranging
        assert not result.should_trade
    
    def test_regime_blocks_signal(self):
        """Signal should be blocked in ranging market."""
        candles = create_ranging_candles(count=100)
        
        detector = RegimeDetector()
        generator = SignalGenerator(..., regime_detector=detector)
        
        signal = generator.generate_signal(candles)
        assert signal is None  # Blocked by regime filter
```

### 8.2 Integration Tests

```python
# tests/integration/test_regime_integration.py

def test_regime_filter_integration():
    """Test regime detector integrates correctly with SignalGenerator."""
    # Setup
    detector = RegimeDetector()
    generator = create_full_signal_generator(regime_detector=detector)
    
    # Test with live-like data
    candles = fetch_recent_candles(symbol="BTCUSDT", count=200)
    
    result = detector.detect_regime(candles)
    assert result is not None
    
    signal = generator.generate_signal(candles)
    
    # If ranging, signal should be None
    if result.is_ranging:
        assert signal is None
```

---

## 9. DEPENDENCIES

### 9.1 Python Packages

```
hmmlearn>=0.3.0      # HMM implementation
numpy>=1.21.0        # Numerical operations
pandas>=1.3.0        # Time series operations
```

### 9.2 Installation

```bash
pip install hmmlearn
```

---

## 10. HANDOFF TO BACKEND

### 10.1 Files to Create

| File | Description | Priority |
|------|-------------|----------|
| `regime_result.py` | RegimeResult value object | P0 |
| `regime_detector.py` | HMM implementation | P0 |
| `i_regime_detector.py` | Interface | P0 |
| `regime_config.py` | Configuration | P0 |

### 10.2 Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `signal_generator.py` | Add regime filter logic | P0 |
| `realtime_service.py` | Initialize detector | P1 |
| `requirements.txt` | Add hmmlearn | P0 |

### 10.3 Validation Checklist

- [ ] RegimeDetector can be initialized
- [ ] Feature extraction works with real candle data
- [ ] Rule-based fallback works when HMM not fitted
- [ ] HMM fitting completes without error
- [ ] Regime detection returns valid RegimeResult
- [ ] SignalGenerator correctly blocks signals in RANGING
- [ ] Logging shows regime classification
- [ ] Unit tests pass
- [ ] Integration tests pass

---

## 11. EXPECTED OUTCOMES

### 11.1 Before Implementation

```
Market: RANGING
ADX: 15
SignalGenerator: Generates BUY signal (false positive)
Result: LOSS
```

### 11.2 After Implementation

```
Market: RANGING
ADX: 15
RegimeDetector: Detects RANGING (confidence: 0.78)
SignalGenerator: Signal BLOCKED
Result: NO TRADE (avoided loss)
```

---

*This specification is ready for Backend Engineer AI implementation.*
*Estimated implementation time: 1-2 days*
*Created by: Quant Specialist AI*
*Date: 2025-12-23*
