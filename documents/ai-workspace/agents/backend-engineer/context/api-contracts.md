# 📡 API CONTRACTS - Hinto Stock

**Last Updated:** 2025-12-22
**Owner:** Backend Engineer

---

## 1. BASE CONFIGURATION

```yaml
Base URL: /api/v1
Content-Type: application/json
Authentication: Bearer Token (future)
```

---

## 2. SIGNAL ENDPOINTS

### GET /signals/active
Get all active trading signals.

```yaml
Request:
  method: GET
  query_params:
    symbol: string (optional) - Filter by symbol
    layer: integer (optional) - 1, 2, or 3

Response 200:
  {
    "signals": [
      {
        "id": "sig_123",
        "symbol": "BTCUSDT",
        "layer": 1,
        "direction": "LONG",
        "entry_price": 97500.50,
        "stop_loss": 96800.00,
        "take_profit": 98500.00,
        "confidence": 0.75,
        "status": "ACTIVE",
        "created_at": "2025-12-22T08:00:00Z",
        "expires_at": "2025-12-22T08:05:00Z",
        "indicators": {
          "vwap": 97200.00,
          "bb_upper": 98200.00,
          "bb_lower": 96500.00,
          "stoch_rsi_k": 25.5,
          "stoch_rsi_d": 22.3
        }
      }
    ],
    "count": 1,
    "timestamp": "2025-12-22T08:00:15Z"
  }
```

### GET /signals/{signal_id}
Get specific signal details.

```yaml
Response 200:
  {
    "signal": { ... },  // Same structure as above
    "history": [
      {
        "event": "CREATED",
        "timestamp": "2025-12-22T08:00:00Z"
      },
      {
        "event": "ENTRY_HIT",
        "timestamp": "2025-12-22T08:02:30Z",
        "price": 97480.00
      }
    ]
  }

Response 404:
  {
    "error": "Signal not found",
    "code": "SIGNAL_NOT_FOUND"
  }
```

---

## 3. MARKET DATA ENDPOINTS

### GET /market/price/{symbol}
Get current price for symbol.

```yaml
Response 200:
  {
    "symbol": "BTCUSDT",
    "price": 97500.50,
    "change_24h": 2.35,
    "volume_24h": 1234567890.50,
    "timestamp": "2025-12-22T08:00:00Z"
  }
```

### GET /market/candles/{symbol}
Get historical candles.

```yaml
Request:
  query_params:
    interval: string - "1m", "5m", "15m", "1H"
    limit: integer - Max 1000, default 100
    start_time: string (optional) - ISO 8601
    end_time: string (optional) - ISO 8601

Response 200:
  {
    "symbol": "BTCUSDT",
    "interval": "5m",
    "candles": [
      {
        "open_time": "2025-12-22T07:55:00Z",
        "close_time": "2025-12-22T07:59:59Z",
        "open": 97400.00,
        "high": 97550.00,
        "low": 97350.00,
        "close": 97500.00,
        "volume": 123.45
      }
    ],
    "count": 100
  }
```

### GET /market/indicators/{symbol}
Get calculated indicators.

```yaml
Request:
  query_params:
    indicators: string[] - ["vwap", "bb", "stochrsi"]
    interval: string - "5m"

Response 200:
  {
    "symbol": "BTCUSDT",
    "interval": "5m",
    "timestamp": "2025-12-22T08:00:00Z",
    "indicators": {
      "vwap": {
        "value": 97200.00
      },
      "bollinger_bands": {
        "upper": 98200.00,
        "middle": 97200.00,
        "lower": 96200.00
      },
      "stoch_rsi": {
        "k": 25.5,
        "d": 22.3
      }
    }
  }
```

---

## 4. ORDER ENDPOINTS

### POST /orders
Place a new order.

```yaml
Request:
  {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": 0.01,
    "price": 97400.00,
    "stop_loss": 96800.00,
    "take_profit": 98500.00,
    "signal_id": "sig_123" (optional)
  }

Response 201:
  {
    "order_id": "ord_456",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": 0.01,
    "price": 97400.00,
    "status": "PENDING",
    "created_at": "2025-12-22T08:01:00Z"
  }

Response 400:
  {
    "error": "Insufficient margin",
    "code": "INSUFFICIENT_MARGIN",
    "required": 500.00,
    "available": 250.00
  }
```

### GET /orders/open
Get all open orders.

### DELETE /orders/{order_id}
Cancel an order.

---

## 5. POSITION ENDPOINTS

### GET /positions
Get all open positions.

```yaml
Response 200:
  {
    "positions": [
      {
        "id": "pos_789",
        "symbol": "BTCUSDT",
        "side": "LONG",
        "entry_price": 97400.00,
        "quantity": 0.01,
        "unrealized_pnl": 1.00,
        "margin": 48.70,
        "leverage": 20,
        "liquidation_price": 92500.00,
        "created_at": "2025-12-22T08:02:00Z"
      }
    ],
    "total_margin": 48.70,
    "total_pnl": 1.00
  }
```

### POST /positions/{position_id}/close
Close a position.

---

## 6. ACCOUNT ENDPOINTS

### GET /account/balance
Get account balance.

```yaml
Response 200:
  {
    "balance": {
      "total": 1000.00,
      "available": 951.30,
      "in_positions": 48.70
    },
    "currency": "USDT"
  }
```

### GET /account/stats
Get trading statistics.

```yaml
Response 200:
  {
    "stats": {
      "total_trades": 50,
      "winning_trades": 30,
      "losing_trades": 20,
      "win_rate": 0.60,
      "profit_factor": 1.8,
      "total_pnl": 150.00,
      "max_drawdown": 0.08
    },
    "period": "30d"
  }
```

---

## 7. WEBSOCKET EVENTS

### Connection
```
ws://localhost:8000/ws
```

### Events (Server → Client)

```typescript
// Price update
{
  "type": "price:update",
  "data": {
    "symbol": "BTCUSDT",
    "price": 97500.50,
    "timestamp": "2025-12-22T08:00:00Z"
  }
}

// New signal
{
  "type": "signal:new",
  "data": {
    "id": "sig_123",
    "symbol": "BTCUSDT",
    "direction": "LONG",
    ...
  }
}

// Signal expired
{
  "type": "signal:expired",
  "data": {
    "id": "sig_123",
    "reason": "TIMEOUT"
  }
}

// Position update
{
  "type": "position:update",
  "data": {
    "id": "pos_789",
    "unrealized_pnl": 2.50,
    ...
  }
}
```

---

## 8. ERROR CODES

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request |
| `INSUFFICIENT_MARGIN` | 400 | Not enough margin |
| `INVALID_SYMBOL` | 400 | Unknown symbol |
| `SIGNAL_NOT_FOUND` | 404 | Signal doesn't exist |
| `ORDER_NOT_FOUND` | 404 | Order doesn't exist |
| `POSITION_NOT_FOUND` | 404 | Position doesn't exist |
| `RATE_LIMITED` | 429 | Too many requests |
| `EXCHANGE_ERROR` | 502 | Exchange API error |
| `INTERNAL_ERROR` | 500 | Server error |

---

**Status:** 🟡 Draft - Awaiting implementation
