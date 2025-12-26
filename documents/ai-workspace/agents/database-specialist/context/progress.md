# Database Specialist Context - Current Codebase State

Version: 1.0 | Updated: 2025-12-22
Based on: Actual codebase audit

---

## DATABASE OVERVIEW

Database: SQLite
Location: data/trading_system.db (77KB)
ORM: Raw sqlite3 (no SQLAlchemy yet)
Pattern: Repository Pattern

---

## PERSISTENCE LAYER

Location: src/infrastructure/persistence/

### Repositories

| Repository | File | Lines | Purpose |
|------------|------|-------|---------|
| SQLiteMarketDataRepository | sqlite_market_data_repository.py | 301 | Candles, indicators |
| SQLiteOrderRepository | sqlite_order_repository.py | 297 | Positions, orders, settings |
| SQLiteStateRepository | sqlite_state_repository.py | ~150 | State machine persistence |

---

## SCHEMA (Inferred from code)

### candles_{timeframe} Tables
```sql
CREATE TABLE IF NOT EXISTS candles_1m (
    timestamp TEXT PRIMARY KEY,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    -- Indicator columns
    rsi REAL,
    vwap REAL,
    upper_band REAL,
    lower_band REAL,
    middle_band REAL
);
-- Similar for: candles_15m, candles_1h
```

### positions Table
```sql
CREATE TABLE IF NOT EXISTS positions (
    id TEXT PRIMARY KEY,
    symbol TEXT,
    side TEXT,              -- LONG/SHORT
    status TEXT,            -- PENDING/OPEN/CLOSED
    entry_price REAL,
    exit_price REAL,
    quantity REAL,
    leverage INTEGER,
    stop_loss REAL,
    take_profit REAL,
    realized_pnl REAL,
    unrealized_pnl REAL,
    created_at TEXT,
    updated_at TEXT,
    closed_at TEXT,
    metadata TEXT           -- JSON for extra data
);
```

### account Table
```sql
CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY,
    balance REAL,
    updated_at TEXT
);
```

### settings Table
```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

---

## DATA FILES

| File | Size | Purpose |
|------|------|---------|
| data/trading_system.db | 77KB | Main trading database |
| data/btc_15m.csv | 600KB | Historical BTC 15m candles |

---

## REPOSITORY METHODS

### SQLiteMarketDataRepository
- save_candle(candle, indicator, timeframe)
- save_market_data(market_data)
- get_latest_candles(timeframe, limit)
- get_candles_by_date_range(timeframe, start, end)
- get_candle_by_timestamp(timeframe, timestamp)
- get_record_count(timeframe)
- get_latest_timestamp(timeframe)
- delete_candles_before(timeframe, before)
- get_database_size()
- backup_database(backup_path)
- get_table_info(timeframe)

### SQLiteOrderRepository
- save_order(position)
- update_order(position)
- get_order(position_id)
- get_active_orders()
- get_pending_orders()
- get_closed_orders(limit)
- get_closed_orders_paginated(page, limit)
- get_account_balance()
- update_account_balance(balance)
- reset_database()
- get_setting(key)
- set_setting(key, value)
- get_all_settings()

---

## INTERFACE CONTRACTS

Location: src/domain/repositories/

| Interface | Implementation |
|-----------|----------------|
| MarketDataRepository | SQLiteMarketDataRepository |
| IOrderRepository | SQLiteOrderRepository |

---

## KNOWN LIMITATIONS

| Issue | Impact | Status |
|-------|--------|--------|
| No SQLAlchemy | Manual SQL, less type safety | Low priority |
| No migrations | Schema changes need manual handling | Medium |
| Single connection | No connection pooling | Low (desktop app) |

---

## FUTURE MIGRATION PATH

If scaling to PostgreSQL:
1. Add SQLAlchemy models
2. Create Alembic migrations
3. Implement PostgreSQL repositories
4. Keep SQLite for desktop, PostgreSQL for cloud

---

## HOW TO ACCESS

```python
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.infrastructure.persistence.sqlite_market_data_repository import SQLiteMarketDataRepository

# Initialize
order_repo = SQLiteOrderRepository("data/trading_system.db")
market_repo = SQLiteMarketDataRepository("data/crypto_data.db")

# Use
balance = order_repo.get_account_balance()
candles = market_repo.get_latest_candles("1m", limit=100)
```
