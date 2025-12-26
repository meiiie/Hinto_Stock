# ⚡ DATABASE OPTIMIZATION NOTES

**Last Updated:** 2025-12-22
**Owner:** Database Specialist

---

## PERFORMANCE TARGETS

| Metric | Target | Current |
|--------|--------|---------|
| Candle query (100 rows) | < 10ms | TBD |
| Signal insert | < 5ms | TBD |
| Active signals query | < 5ms | TBD |
| Trade history (1000 rows) | < 50ms | TBD |

---

## OPTIMIZATION STRATEGIES

### 1. Indexing Strategy

**Primary Indexes:**
```sql
-- Most critical: Candle lookup
CREATE INDEX idx_candles_lookup 
    ON candle_data(symbol, interval, open_time DESC);

-- Active signals (partial index)
CREATE INDEX idx_signals_active 
    ON signals(status, created_at DESC) 
    WHERE status = 'ACTIVE';
```

**Considerations:**
- Avoid over-indexing (insert performance)
- Monitor index usage with EXPLAIN QUERY PLAN
- Rebuild indexes periodically

### 2. Query Optimization

**DO:**
```sql
-- Use indexed columns first
SELECT * FROM candle_data 
WHERE symbol = 'BTCUSDT' AND interval = '5m'
ORDER BY open_time DESC LIMIT 100;

-- Use EXISTS for checking
SELECT EXISTS(
    SELECT 1 FROM signals WHERE status = 'ACTIVE' AND symbol = ?
);
```

**DON'T:**
```sql
-- Avoid functions on indexed columns
SELECT * FROM candle_data 
WHERE DATE(open_time) = '2025-12-22';  -- Index not used!

-- Avoid SELECT *
SELECT * FROM trades;  -- Fetch only needed columns
```

### 3. Connection Pooling

For Desktop app (SQLite):
- Single connection sufficient
- Consider WAL mode for concurrent reads

```python
# Enable WAL mode
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-64000;  # 64MB cache
```

### 4. Data Archival

```python
# Archive old data to reduce table size
def archive_old_data():
    # Move candles older than 30 days to archive
    cursor.execute("""
        INSERT INTO candle_data_archive 
        SELECT * FROM candle_data 
        WHERE open_time < datetime('now', '-30 days');
        
        DELETE FROM candle_data 
        WHERE open_time < datetime('now', '-30 days');
    """)
```

---

## BENCHMARK RESULTS

### 2025-12-22: Initial Baseline

| Query | Time | Notes |
|-------|------|-------|
| - | - | No benchmarks yet |

---

## MONITORING QUERIES

```sql
-- Table sizes
SELECT 
    name,
    (page_count * page_size) / 1024 / 1024 AS size_mb
FROM sqlite_master
JOIN pragma_page_count(name) ON 1=1
JOIN pragma_page_size ON 1=1
WHERE type = 'table';

-- Index usage (after queries)
EXPLAIN QUERY PLAN 
SELECT * FROM candle_data 
WHERE symbol = 'BTCUSDT' AND interval = '5m';
```

---

## FUTURE CONSIDERATIONS

### If scaling needed:
1. **PostgreSQL migration**
   - TimescaleDB for time-series optimization
   - Connection pooling with PgBouncer
   
2. **Partitioning**
   - Partition candle_data by date range
   - Partition trades by month

3. **Caching layer**
   - Redis for hot data (current prices)
   - Reduce DB load for frequent queries

---

**Next Review:** After initial performance testing
