# QA Engineer Context - Current Codebase State

Version: 1.0 | Updated: 2025-12-22
Based on: Actual codebase audit

---

## TESTING OVERVIEW

Backend: Pytest
Frontend: Vitest 2.1.9
Property Testing: fast-check (frontend), hypothesis (backend)
Config: pytest.ini, vitest.config.ts

---

## TEST STRUCTURE

```
tests/
|-- __init__.py
|-- architecture/           # Architecture tests (4 files)
|-- integration/            # Integration tests (3 files)
|   |-- test_backend_flow.py
|   |-- test_full_system.py
|   +-- __init__.py
|-- property/               # Property-based tests (9 files)
|-- unit/                   # Unit tests (1 file)
|
|-- test_adx_calculator.py        # ADX indicator tests (14KB)
|-- test_aggregator.py            # Candle aggregation tests (6KB)
|-- test_atr_calculator.py        # ATR indicator tests (11KB)
|-- test_config.py                # Config tests (8KB)
|-- test_domain_entities.py       # Entity tests (14KB)
|-- test_rsi_monitor.py           # RSI monitor tests (7KB)
|-- test_signal_generator_integration.py  # Signal integration (16KB)
|-- test_signal_generator_strict.py       # Strict signal tests (17KB)
|-- test_signal_integration.py            # Signal tests (4KB)
|-- test_stop_loss_atr.py         # Stop loss tests (12KB)
|-- test_tp_atr.py                # Take profit tests (10KB)
|-- test_trend_filter.py          # Trend filter tests (14KB)
+-- test_volume_analyzer.py       # Volume analyzer tests (5KB)
```

---

## TEST COVERAGE BY COMPONENT

### Indicators (Well Tested)
| Component | Test File | Lines |
|-----------|-----------|-------|
| ADX Calculator | test_adx_calculator.py | 14KB |
| ATR Calculator | test_atr_calculator.py | 11KB |
| Trend Filter | test_trend_filter.py | 14KB |
| Volume Analyzer | test_volume_analyzer.py | 5KB |
| RSI Monitor | test_rsi_monitor.py | 7KB |

### Signal Generation (Well Tested)
| Component | Test File | Lines |
|-----------|-----------|-------|
| Signal Generator | test_signal_generator_strict.py | 17KB |
| Signal Integration | test_signal_generator_integration.py | 16KB |
| Signal Flow | test_signal_integration.py | 4KB |

### Risk Management (Tested)
| Component | Test File | Lines |
|-----------|-----------|-------|
| Stop Loss | test_stop_loss_atr.py | 12KB |
| Take Profit | test_tp_atr.py | 10KB |

### Domain (Tested)
| Component | Test File | Lines |
|-----------|-----------|-------|
| Entities | test_domain_entities.py | 14KB |
| Aggregator | test_aggregator.py | 6KB |
| Config | test_config.py | 8KB |

---

## TEST CATEGORIES

### Architecture Tests (tests/architecture/)
- Dependency rule verification
- Layer boundary checks
- 4 test files

### Integration Tests (tests/integration/)
- test_backend_flow.py - End-to-end backend flow
- test_full_system.py - Full system integration

### Property-Based Tests (tests/property/)
- 9 test files
- Using hypothesis for fuzzing
- Edge case discovery

### Unit Tests (tests/unit/)
- Component isolation tests

---

## HOW TO RUN TESTS

### Backend (Pytest)
```bash
# All tests
pytest

# Specific test file
pytest tests/test_adx_calculator.py

# With coverage
pytest --cov=src

# Verbose
pytest -v
```

### Frontend (Vitest)
```bash
cd frontend

# Run once
npm run test

# Watch mode
npm run test:watch
```

---

## KNOWN ISSUES TO TEST

| Issue | Test Type | Priority |
|-------|-----------|----------|
| Sign trade not working | Integration | High |
| Signal Panel not updating | E2E | Medium |
| WebSocket reconnection | Integration | Medium |

---

## TESTING GAPS

| Area | Current | Recommended |
|------|---------|-------------|
| Frontend components | None visible | Add React Testing Library |
| WebSocket | No tests | Add mock WebSocket tests |
| Paper Trading | No dedicated tests | Add paper trading flow tests |
| E2E | Basic | Add Playwright for full E2E |

---

## TEST CONFIGURATION

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v
```

### vitest.config.ts
```typescript
// Configuration for Vitest
```

---

## COVERAGE TARGETS

| Layer | Target | Current |
|-------|--------|---------|
| Domain | 95% | Unknown |
| Application | 85% | Unknown |
| Infrastructure | 70% | Unknown |
| API | 80% | Unknown |

---

## NEXT TESTING PRIORITIES

1. Add test for "sign trade" bug
2. Add WebSocket mock tests
3. Add Paper Trading flow tests
4. Set up coverage reporting
5. Add E2E tests with Playwright
