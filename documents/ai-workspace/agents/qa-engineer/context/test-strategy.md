# 🧪 TEST STRATEGY - Hinto Stock

**Last Updated:** 2025-12-22
**Owner:** QA Engineer

---

## 1. TESTING OBJECTIVES

- Ensure trading logic accuracy (critical for financial operations)
- Verify signal generation correctness
- Validate risk management rules
- Confirm UI responsiveness for real-time data
- Prevent regressions during refactoring

---

## 2. TEST PYRAMID

```
           ┌─────────┐
          │   E2E   │  10% - Critical user journeys
         │  Tests  │
      ┌───────────────┐
     │  Integration  │  30% - API & component interaction
    │     Tests     │
 ┌─────────────────────┐
│      Unit Tests      │  60% - Business logic, utilities
│                       │
└─────────────────────────┘
```

---

## 3. COVERAGE TARGETS

| Component | Target | Priority |
|-----------|--------|----------|
| Signal Generator | 95% | 🔴 Critical |
| Risk Manager | 95% | 🔴 Critical |
| Position Calculator | 90% | 🔴 Critical |
| Order Manager | 90% | 🔴 Critical |
| API Endpoints | 85% | 🟡 High |
| WebSocket Handlers | 80% | 🟡 High |
| UI Components | 70% | 🟢 Medium |
| Utilities | 60% | 🟢 Medium |

---

## 4. TEST CATEGORIES

### 4.1 Unit Tests

**Focus Areas:**
- Indicator calculations (VWAP, BB, StochRSI)
- Signal logic (entry conditions)
- Risk calculations (position size, SL/TP)
- Price utilities (precision, formatting)

**Example Test Cases:**
```
Signal Generator:
├── test_bullish_signal_all_conditions_met
├── test_no_signal_when_below_vwap
├── test_no_signal_when_stochrsi_below_threshold
├── test_no_signal_insufficient_volume
└── test_signal_expiry_after_ttl

Risk Manager:
├── test_position_size_with_1_percent_risk
├── test_stop_loss_swing_based
├── test_stop_loss_atr_fallback
├── test_max_position_limit_enforced
└── test_daily_loss_limit_blocks_trading
```

### 4.2 Integration Tests

**Focus Areas:**
- API request/response
- Database operations
- WebSocket events
- Service interactions

**Example Test Cases:**
```
API Integration:
├── test_get_active_signals_returns_correct_format
├── test_place_order_validates_margin
├── test_close_position_updates_pnl
└── test_websocket_receives_price_updates

Database Integration:
├── test_candle_insert_and_query
├── test_signal_status_transitions
└── test_trade_history_aggregation
```

### 4.3 E2E Tests

**Focus Areas:**
- Critical user journeys
- Trading workflow
- Error handling

**Example Scenarios:**
```
Trading Flow:
├── User sees signal → clicks it → order form opens
├── User places order → sees confirmation → position appears
├── Position hits TP → auto-closed → PnL updated
└── Signal expires → UI updates → no ghost signals

Error Handling:
├── Network disconnect → reconnect → state restored
├── Insufficient margin → error shown → no order placed
└── Exchange timeout → retry → or graceful failure
```

---

## 5. TEST DATA MANAGEMENT

### Mock Data Patterns
```python
# Bullish scenario
BULLISH_MARKET = {
    "candles": [...],  # Price above VWAP, pullback to lower BB
    "indicators": {"vwap": 97000, "stoch_rsi": 25},
    "expected_signal": "LONG"
}

# Bearish scenario
BEARISH_MARKET = {
    "candles": [...],  # Price below VWAP, rally to upper BB
    "indicators": {"vwap": 97000, "stoch_rsi": 82},
    "expected_signal": "SHORT"
}

# No signal scenario
SIDEWAYS_MARKET = {
    "candles": [...],  # Price near VWAP, no clear direction
    "indicators": {"vwap": 97000, "stoch_rsi": 50},
    "expected_signal": None
}
```

### Test Fixtures
- Use pytest fixtures for common setups
- Never use real exchange API in tests
- Mock external dependencies

---

## 6. TRADING-SPECIFIC TEST SCENARIOS

### Edge Cases (Critical)
| Scenario | Test |
|----------|------|
| Rapid price movement | Signal validation still works |
| Gap up/down | SL/TP calculations correct |
| Zero volume candle | No division by zero |
| API rate limit | Graceful degradation |
| Partial fill | Position tracking accurate |
| Network reconnect | State recovery works |

### Risk Scenarios
| Scenario | Expected Behavior |
|----------|-------------------|
| Risk > 1% | Order rejected |
| Daily loss > 5% | Trading paused |
| Leverage > 20x | Order rejected |
| Max positions | New orders rejected |

---

## 7. TEST AUTOMATION

### CI/CD Integration
```yaml
# On every push
- Run unit tests
- Check coverage thresholds
- Lint and type check

# On PR merge
- Run integration tests
- Run E2E tests (subset)
- Performance regression check
```

### Test Commands
```bash
# Unit tests
pytest tests/unit -v --cov=app

# Integration tests
pytest tests/integration -v

# E2E tests
npx playwright test

# All tests with coverage
pytest --cov=app --cov-report=html
```

---

## 8. BUG TRACKING

### Bug Severity Levels
| Level | Definition | Response |
|-------|------------|----------|
| 🔴 Critical | Data loss, wrong trade | Immediate fix |
| 🟠 High | Major feature broken | Same day |
| 🟡 Medium | Feature partially works | Next sprint |
| 🟢 Low | Cosmetic, minor | Backlog |

### Regression Test Strategy
- Critical bugs → Add regression test
- High bugs → Add regression test
- All tests must pass before merge

---

## 9. CURRENT STATUS

### Test Coverage
| Area | Current | Target |
|------|---------|--------|
| Overall | TBD | 80% |
| Domain | TBD | 90% |
| API | TBD | 85% |
| UI | TBD | 70% |

### Known Gaps
1. Signal Generator not fully tested
2. E2E tests not set up yet
3. Performance tests not implemented

---

**Next Review:** After Layer 1 refactor complete
