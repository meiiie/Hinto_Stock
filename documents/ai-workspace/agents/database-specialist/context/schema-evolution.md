# 📜 DATABASE SCHEMA EVOLUTION

**Last Updated:** 2025-12-22
**Owner:** Database Specialist

---

## CURRENT SCHEMA VERSION

**Version:** 1.0
**Database:** SQLite (Desktop deployment)

---

## SCHEMA OVERVIEW

```
┌──────────────────┐     ┌──────────────────┐
│   candle_data    │     │     signals      │
├──────────────────┤     ├──────────────────┤
│ id               │     │ id               │
│ symbol           │     │ symbol           │
│ interval         │     │ layer            │
│ open_time        │     │ direction        │
│ close_time       │     │ entry_price      │
│ open             │     │ stop_loss        │
│ high             │     │ take_profit      │
│ low              │     │ confidence       │
│ close            │     │ status           │
│ volume           │     │ created_at       │
│ created_at       │     │ expired_at       │
└──────────────────┘     └──────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ indicator_cache  │     │     trades       │
├──────────────────┤     ├──────────────────┤
│ id               │     │ id               │
│ symbol           │     │ signal_id (FK)   │
│ interval         │     │ symbol           │
│ timestamp        │     │ side             │
│ indicator_type   │     │ order_type       │
│ value_json       │     │ quantity         │
│ created_at       │     │ price            │
└──────────────────┘     │ fee              │
                         │ pnl              │
                         │ status           │
                         │ executed_at      │
                         │ created_at       │
                         └──────────────────┘
```

---

## TABLE DEFINITIONS

### candle_data
```sql
CREATE TABLE candle_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(5) NOT NULL,
    open_time TIMESTAMP NOT NULL,
    close_time TIMESTAMP NOT NULL,
    open DECIMAL(18, 8) NOT NULL,
    high DECIMAL(18, 8) NOT NULL,
    low DECIMAL(18, 8) NOT NULL,
    close DECIMAL(18, 8) NOT NULL,
    volume DECIMAL(18, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol, interval, open_time)
);

CREATE INDEX idx_candles_lookup 
    ON candle_data(symbol, interval, open_time DESC);
```

### signals
```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    layer INTEGER NOT NULL CHECK (layer IN (1, 2, 3)),
    direction VARCHAR(5) NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    entry_price DECIMAL(18, 8),
    stop_loss DECIMAL(18, 8),
    take_profit DECIMAL(18, 8),
    confidence DECIMAL(5, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    indicators_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP
);

CREATE INDEX idx_signals_active 
    ON signals(status, created_at DESC) WHERE status = 'ACTIVE';
CREATE INDEX idx_signals_symbol 
    ON signals(symbol, created_at DESC);
```

### trades
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER REFERENCES signals(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(5) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type VARCHAR(10) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    fee DECIMAL(18, 8) DEFAULT 0,
    pnl DECIMAL(18, 8),
    status VARCHAR(20) NOT NULL,
    exchange_order_id VARCHAR(50),
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_symbol 
    ON trades(symbol, created_at DESC);
CREATE INDEX idx_trades_status 
    ON trades(status);
```

### indicator_cache (Optional)
```sql
CREATE TABLE indicator_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(5) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    indicator_type VARCHAR(20) NOT NULL,
    value_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol, interval, timestamp, indicator_type)
);
```

---

## MIGRATION HISTORY

| Version | Date | Description | Status |
|---------|------|-------------|--------|
| 1.0 | 2025-12-22 | Initial schema | ✅ Applied |

---

## PENDING MIGRATIONS

None currently planned.

---

## OPTIMIZATION NOTES

### Index Usage
- `candle_data`: Composite index on (symbol, interval, open_time) for fast lookups
- `signals`: Partial index on active signals for quick query

### Query Patterns

**Most Common Queries:**
```sql
-- Get recent candles (hot path)
SELECT * FROM candle_data 
WHERE symbol = ? AND interval = ?
ORDER BY open_time DESC LIMIT 100;

-- Get active signals (hot path)
SELECT * FROM signals 
WHERE status = 'ACTIVE' AND symbol = ?;

-- Daily PnL calculation
SELECT DATE(executed_at), SUM(pnl) 
FROM trades GROUP BY DATE(executed_at);
```

### Data Retention
- Candle data: Keep 30 days rolling for 1m interval
- Candle data: Keep 1 year for 1H+ intervals
- Signals: Archive after 7 days
- Trades: Keep indefinitely

---

## KNOWN ISSUES

1. **SQLite limitations**: For production scale, consider PostgreSQL
2. **Decimal handling**: SQLite stores as TEXT, verify precision

---

**Next Review:** After Layer 1 implementation stable
