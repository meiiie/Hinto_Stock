# 🔒 PROJECT CONSTRAINTS - Hinto Stock

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Applies To:** All AI Agents

---

## 1. PERFORMANCE CONSTRAINTS

### Latency Requirements
| Operation | Max Latency | Priority |
|-----------|-------------|----------|
| Price update → UI display | 100ms | 🔴 Critical |
| Signal generation | 500ms | 🔴 Critical |
| Order placement | 1000ms | 🔴 Critical |
| Historical data query | 2000ms | 🟡 High |
| Chart rendering | 16ms (60fps) | 🟡 High |

### Memory Limits (Desktop App)
| Resource | Limit | Notes |
|----------|-------|-------|
| RAM Usage | < 500MB | Includes Electron overhead |
| Candle History | Max 10,000 | Per symbol/interval |
| Log Retention | 7 days | Auto-rotate |

---

## 2. SECURITY CONSTRAINTS

### Data Protection
```markdown
❌ FORBIDDEN:
- Storing API keys in code
- Logging sensitive data (keys, passwords)
- Sending credentials over unencrypted channels

✅ REQUIRED:
- Environment variables for secrets
- Encrypted storage for API credentials
- HTTPS/WSS only for exchange connections
```

### API Key Handling
```python
# CORRECT
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')

# WRONG ❌
api_key = "abc123xyz"  # Hardcoded
```

---

## 3. CODE QUALITY CONSTRAINTS

### Python Backend
| Rule | Enforcement |
|------|-------------|
| Type hints | Required on all public functions |
| Docstrings | Required on all public classes/methods |
| Max function length | 50 lines |
| Max file length | 400 lines |
| Cyclomatic complexity | Max 10 |

### TypeScript Frontend
| Rule | Enforcement |
|------|-------------|
| Strict mode | Enabled |
| No `any` | Error level |
| Component size | Max 200 lines |
| Props interface | Required |

### Common Rules
- No `TODO` in production code
- No commented-out code blocks
- No magic numbers (use constants)
- No deep nesting (max 4 levels)

---

## 4. TRADING-SPECIFIC CONSTRAINTS

### Risk Limits
| Parameter | Limit | Rationale |
|-----------|-------|-----------|
| Max position size | 10% of balance | Single trade exposure |
| Max leverage | 20x | Capital preservation |
| Max daily trades | 50 | Overtrading prevention |
| Max open positions | 5 | Concentration risk |
| Stop loss required | Always | No open-ended risk |

### Signal Constraints
```python
# Every signal MUST have:
class SignalConstraints:
    MIN_CONFIDENCE = 0.6      # 60% minimum confidence
    MAX_AGE_SECONDS = 300     # Signal expires after 5 min
    REQUIRED_FIELDS = [
        'symbol',
        'direction',  # LONG or SHORT
        'entry_price',
        'stop_loss',
        'take_profit',
        'confidence',
        'timestamp',
    ]
```

### Order Constraints
```python
# Order validation rules
CONSTRAINTS = {
    'min_order_value_usdt': 10,
    'max_order_value_usdt': 10000,
    'price_precision': 8,     # Decimal places
    'quantity_precision': 8,
    'max_slippage_percent': 0.1,
}
```

---

## 5. TECHNOLOGY CONSTRAINTS

### Approved Libraries Only
```markdown
## Backend (Python)
✅ Approved:
- aiohttp, httpx (HTTP clients)
- ccxt (Exchange integration)
- pandas, numpy (Data processing)
- pydantic (Validation)
- sqlalchemy (ORM)

❌ Not Approved without PM review:
- Any ML/AI library (heavy dependencies)
- GUI libraries (desktop handled by Electron)
- Third-party trading bots

## Frontend (TypeScript)
✅ Approved:
- react, react-dom
- zustand, jotai (State)
- tailwindcss (Styling)
- lightweight-charts (Trading charts)
- lucide-react (Icons)

❌ Restricted:
- Redux (use zustand instead)
- Moment.js (use date-fns)
- jQuery (not needed)
```

### Version Pinning
```markdown
All dependencies MUST be version-pinned in:
- pyproject.toml or requirements.txt (Backend)
- package.json with exact versions (Frontend)

Example:
✅ "react": "18.2.0"
❌ "react": "^18.2.0"
```

---

## 6. ARCHITECTURAL CONSTRAINTS

### Dependency Rules
```
┌─────────────────────────────────────────────────┐
│                ALLOWED DEPENDENCIES             │
├───────────────┬─────────────────────────────────┤
│ Domain Layer  │ → Nothing (pure business logic) │
├───────────────┼─────────────────────────────────┤
│ Application   │ → Domain only                   │
├───────────────┼─────────────────────────────────┤
│ Infrastructure│ → Domain, Application           │
├───────────────┼─────────────────────────────────┤
│ Presentation  │ → Application only              │
└───────────────┴─────────────────────────────────┘

❌ FORBIDDEN:
- Domain importing from Infrastructure
- Presentation directly accessing Domain
- Circular dependencies between layers
```

### File Organization
```markdown
Every new feature MUST:
1. Add entity to /domain/entities/
2. Add repository interface to /domain/repositories/
3. Add use case to /application/use_cases/
4. Add implementation to /infrastructure/
5. Add tests to /tests/

NO feature code in /utils or /helpers catchall folders
```

---

## 7. TESTING CONSTRAINTS

### Coverage Requirements
| Layer | Minimum Coverage |
|-------|------------------|
| Domain Services | 90% |
| Use Cases | 80% |
| Infrastructure | 70% |
| UI Components | 60% |

### Test Requirements
```markdown
Before merging:
- [ ] All existing tests pass
- [ ] New code has tests
- [ ] No test uses real exchange API
- [ ] E2E tests for user-facing features
```

---

## 8. DOCUMENTATION CONSTRAINTS

### Required Documentation
| Change Type | Required Docs |
|-------------|---------------|
| New Feature | README section + API doc |
| Bug Fix | Bug report reference |
| Refactor | Migration notes if breaking |
| Dependency | Justification in PR |

### API Documentation
Every endpoint MUST document:
- Request/Response schema
- Error codes
- Example usage
- Rate limits (if applicable)

---

## 9. DEPLOYMENT CONSTRAINTS

### Build Requirements
```markdown
- Desktop app must build for: Windows, macOS, Linux
- Build size: < 200MB installer
- Startup time: < 5 seconds
- Offline capability: Basic UI should work offline
```

### Update Policy
```markdown
- Auto-update check on startup
- User consent before update
- Rollback capability
- No forced updates during active trading
```

---

**IMPORTANT:** Violating these constraints requires explicit approval from Project Manager and documented justification.
