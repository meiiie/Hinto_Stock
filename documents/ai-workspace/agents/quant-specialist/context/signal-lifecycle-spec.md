# 📋 SIGNAL LIFECYCLE SERVICE - Technical Specification v1.0

> **Quant Specialist AI → Backend Engineer AI Handoff**  
> Created: 2025-12-23  
> Priority: P0 (Critical Gap)  
> Expected Impact: Complete audit trail, signal→order traceability

---

## 1. EXECUTIVE SUMMARY

### 1.1 Problem Statement

Trading signals are currently **ephemeral** - generated, broadcast via WebSocket, but never persisted. This creates critical gaps:
- No history of signals generated
- No tracking of which signals were executed vs ignored
- No linkage between signals and resulting orders
- No audit trail for compliance/analysis

### 1.2 Solution

Implement a **Signal Lifecycle Service** that:
- Assigns unique IDs to every signal
- Persists signals to database
- Tracks status transitions: GENERATED → PENDING → EXECUTED/EXPIRED
- Links signal_id to order_id for full traceability

### 1.3 Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Signal Persistence | ❌ None | ✅ All signals |
| Signal→Order Link | ❌ None | ✅ 100% linked |
| Execution Latency Tracking | ❌ No | ✅ ms precision |
| Historical Query | ❌ No | ✅ Last 30 days |

---

## 2. ARCHITECTURE

### 2.1 System Integration

```
┌──────────────────────────────────────────────────────────────────────┐
│                        TRADING SYSTEM                                 │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │       LAYER -1: SIGNAL LIFECYCLE (NEW)                       │    │
│  │  ┌────────────────────────────────────────────────────────┐  │    │
│  │  │            SignalLifecycleService                       │  │    │
│  │  │  - Assign UUID to every signal                         │  │    │
│  │  │  - Persist to SignalRepository                         │  │    │
│  │  │  - Track status: GENERATED → PENDING → EXECUTED        │  │    │
│  │  │  - Link signal_id ↔ order_id                           │  │    │
│  │  └────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │       LAYER 0: REGIME FILTER (Implemented)                   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │       LAYER 1: SIGNAL GENERATION (Existing)                  │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │       LAYER 2: EXECUTION (Existing)                          │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 File Structure

```
src/
├── domain/
│   ├── entities/
│   │   └── trading_signal.py          # MODIFY: Add id, status, outcome
│   ├── value_objects/
│   │   └── signal_status.py           # NEW: SignalStatus enum
│   └── repositories/
│       └── i_signal_repository.py     # NEW: Signal persistence interface
├── infrastructure/
│   └── repositories/
│       └── sqlite_signal_repository.py # NEW: SQLite implementation
└── application/
    └── services/
        └── signal_lifecycle_service.py # NEW: Lifecycle orchestration
```

---

## 3. DOMAIN MODEL

### 3.1 SignalStatus Enum

```python
# src/domain/value_objects/signal_status.py

from enum import Enum

class SignalStatus(Enum):
    """Signal lifecycle status transitions."""
    
    GENERATED = "generated"   # Just created by SignalGenerator
    PENDING = "pending"       # Sent to frontend, awaiting action
    EXECUTED = "executed"     # Order created from this signal
    EXPIRED = "expired"       # TTL exceeded without action
    REJECTED = "rejected"     # Filtered by regime/hard filters
    CANCELLED = "cancelled"   # User or system cancelled
```

### 3.2 Enhanced TradingSignal Entity

```python
# src/domain/entities/trading_signal.py (ENHANCED)

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from .signal_status import SignalStatus


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


@dataclass
class TradingSignal:
    """
    Trading signal with full lifecycle tracking.
    
    NEW Fields:
        id: Unique identifier (UUID)
        status: Current lifecycle status
        generated_at: Original generation timestamp
        pending_at: When shown to user
        executed_at: When order was created
        expired_at: When signal expired
        order_id: Linked order ID (if executed)
        outcome: Trade outcome (if completed)
    """
    # Core fields (existing)
    signal_type: SignalType
    confidence: float
    price: float
    indicators: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    
    # Enhanced signal fields (existing)
    entry_price: Optional[float] = None
    tp_levels: Optional[Dict[str, float]] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    # NEW: Lifecycle tracking fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: SignalStatus = SignalStatus.GENERATED
    
    # NEW: Timestamps for each transition
    generated_at: datetime = field(default_factory=datetime.now)
    pending_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    # NEW: Linkage to order
    order_id: Optional[str] = None
    
    # NEW: Outcome tracking (set after trade closes)
    outcome: Optional[Dict[str, Any]] = None
    
    # DEPRECATED: Use generated_at instead
    @property
    def timestamp(self) -> datetime:
        """Backward compatibility: returns generated_at."""
        return self.generated_at
    
    # Lifecycle methods
    def mark_pending(self) -> None:
        """Mark signal as shown to user."""
        self.status = SignalStatus.PENDING
        self.pending_at = datetime.now()
    
    def mark_executed(self, order_id: str) -> None:
        """Mark signal as executed with order link."""
        self.status = SignalStatus.EXECUTED
        self.executed_at = datetime.now()
        self.order_id = order_id
    
    def mark_expired(self) -> None:
        """Mark signal as expired."""
        self.status = SignalStatus.EXPIRED
        self.expired_at = datetime.now()
    
    def mark_rejected(self, reason: str) -> None:
        """Mark signal as rejected by filter."""
        self.status = SignalStatus.REJECTED
        self.reasons.append(f"REJECTED: {reason}")
    
    @property
    def execution_latency_ms(self) -> Optional[float]:
        """Time from generation to execution in milliseconds."""
        if self.generated_at and self.executed_at:
            delta = self.executed_at - self.generated_at
            return delta.total_seconds() * 1000
        return None
    
    @property
    def is_actionable(self) -> bool:
        """Check if signal can still be executed."""
        return self.status in [SignalStatus.GENERATED, SignalStatus.PENDING]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API response."""
        return {
            "id": self.id,
            "signal_type": self.signal_type.value,
            "status": self.status.value,
            "confidence": self.confidence,
            "price": self.price,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "tp_levels": self.tp_levels,
            "indicators": self.indicators,
            "reasons": self.reasons,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "pending_at": self.pending_at.isoformat() if self.pending_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "expired_at": self.expired_at.isoformat() if self.expired_at else None,
            "order_id": self.order_id,
            "execution_latency_ms": self.execution_latency_ms,
            "outcome": self.outcome
        }
```

---

## 4. REPOSITORY INTERFACE

### 4.1 ISignalRepository

```python
# src/domain/repositories/i_signal_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.trading_signal import TradingSignal
from ..value_objects.signal_status import SignalStatus


class ISignalRepository(ABC):
    """Interface for signal persistence."""
    
    @abstractmethod
    def save(self, signal: TradingSignal) -> None:
        """Persist a signal."""
        pass
    
    @abstractmethod
    def update(self, signal: TradingSignal) -> None:
        """Update existing signal."""
        pass
    
    @abstractmethod
    def get_by_id(self, signal_id: str) -> Optional[TradingSignal]:
        """Get signal by ID."""
        pass
    
    @abstractmethod
    def get_by_status(
        self, 
        status: SignalStatus, 
        limit: int = 50
    ) -> List[TradingSignal]:
        """Get signals by status."""
        pass
    
    @abstractmethod
    def get_by_order_id(self, order_id: str) -> Optional[TradingSignal]:
        """Get signal linked to an order."""
        pass
    
    @abstractmethod
    def get_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TradingSignal]:
        """Get signal history with pagination."""
        pass
    
    @abstractmethod
    def get_pending_count(self) -> int:
        """Count pending signals."""
        pass
    
    @abstractmethod
    def expire_old_pending(self, ttl_seconds: int = 300) -> int:
        """Expire pending signals older than TTL. Returns count expired."""
        pass
```

---

## 5. SQLITE IMPLEMENTATION

### 5.1 Database Schema

```sql
-- signals table
CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL DEFAULT 'BTCUSDT',
    signal_type TEXT NOT NULL,  -- 'buy', 'sell', 'neutral'
    status TEXT NOT NULL,       -- 'generated', 'pending', 'executed', etc.
    confidence REAL NOT NULL,
    price REAL NOT NULL,
    entry_price REAL,
    stop_loss REAL,
    tp1 REAL,
    tp2 REAL,
    tp3 REAL,
    position_size REAL,
    risk_reward_ratio REAL,
    
    -- Timestamps
    generated_at TIMESTAMP NOT NULL,
    pending_at TIMESTAMP,
    executed_at TIMESTAMP,
    expired_at TIMESTAMP,
    
    -- Linkage
    order_id TEXT,
    
    -- Audit
    indicators_json TEXT,  -- JSON blob
    reasons_json TEXT,     -- JSON array
    outcome_json TEXT,     -- JSON blob
    
    -- Indexes
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_generated_at ON signals(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_order_id ON signals(order_id);
```

### 5.2 Repository Implementation

```python
# src/infrastructure/repositories/sqlite_signal_repository.py

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional

from src.domain.entities.trading_signal import TradingSignal, SignalType
from src.domain.value_objects.signal_status import SignalStatus
from src.domain.repositories.i_signal_repository import ISignalRepository


class SQLiteSignalRepository(ISignalRepository):
    """SQLite implementation of signal repository."""
    
    def __init__(self, db_path: str = "data/paper_trading.db"):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self) -> None:
        """Create signals table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL DEFAULT 'BTCUSDT',
                signal_type TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                price REAL NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                tp1 REAL,
                tp2 REAL,
                tp3 REAL,
                position_size REAL,
                risk_reward_ratio REAL,
                generated_at TIMESTAMP NOT NULL,
                pending_at TIMESTAMP,
                executed_at TIMESTAMP,
                expired_at TIMESTAMP,
                order_id TEXT,
                indicators_json TEXT,
                reasons_json TEXT,
                outcome_json TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_status 
            ON signals(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_generated_at 
            ON signals(generated_at DESC)
        """)
        conn.commit()
        conn.close()
    
    def save(self, signal: TradingSignal) -> None:
        """Persist a new signal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tp_levels = signal.tp_levels or {}
        
        cursor.execute("""
            INSERT INTO signals (
                id, signal_type, status, confidence, price,
                entry_price, stop_loss, tp1, tp2, tp3,
                position_size, risk_reward_ratio,
                generated_at, pending_at, executed_at, expired_at,
                order_id, indicators_json, reasons_json, outcome_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal.id,
            signal.signal_type.value,
            signal.status.value,
            signal.confidence,
            signal.price,
            signal.entry_price,
            signal.stop_loss,
            tp_levels.get('tp1'),
            tp_levels.get('tp2'),
            tp_levels.get('tp3'),
            signal.position_size,
            signal.risk_reward_ratio,
            signal.generated_at.isoformat(),
            signal.pending_at.isoformat() if signal.pending_at else None,
            signal.executed_at.isoformat() if signal.executed_at else None,
            signal.expired_at.isoformat() if signal.expired_at else None,
            signal.order_id,
            json.dumps(signal.indicators),
            json.dumps(signal.reasons),
            json.dumps(signal.outcome) if signal.outcome else None
        ))
        
        conn.commit()
        conn.close()
    
    def update(self, signal: TradingSignal) -> None:
        """Update existing signal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE signals SET
                status = ?,
                pending_at = ?,
                executed_at = ?,
                expired_at = ?,
                order_id = ?,
                outcome_json = ?
            WHERE id = ?
        """, (
            signal.status.value,
            signal.pending_at.isoformat() if signal.pending_at else None,
            signal.executed_at.isoformat() if signal.executed_at else None,
            signal.expired_at.isoformat() if signal.expired_at else None,
            signal.order_id,
            json.dumps(signal.outcome) if signal.outcome else None,
            signal.id
        ))
        
        conn.commit()
        conn.close()
    
    # ... other methods implementation
```

---

## 6. SIGNAL LIFECYCLE SERVICE

### 6.1 Service Implementation

```python
# src/application/services/signal_lifecycle_service.py

import logging
from typing import Optional, List
from datetime import datetime, timedelta

from src.domain.entities.trading_signal import TradingSignal
from src.domain.value_objects.signal_status import SignalStatus
from src.domain.repositories.i_signal_repository import ISignalRepository


class SignalLifecycleService:
    """
    Manages the full lifecycle of trading signals.
    
    Responsibilities:
    1. Assign IDs and persist new signals
    2. Track status transitions
    3. Link signals to orders
    4. Expire stale signals
    5. Provide query interface for history
    """
    
    # Signal TTL before expiration (5 minutes default)
    DEFAULT_TTL_SECONDS = 300
    
    def __init__(
        self,
        signal_repository: ISignalRepository,
        ttl_seconds: int = DEFAULT_TTL_SECONDS
    ):
        self.repo = signal_repository
        self.ttl_seconds = ttl_seconds
        self.logger = logging.getLogger(__name__)
    
    def register_signal(self, signal: TradingSignal) -> TradingSignal:
        """
        Register a newly generated signal.
        
        - Assigns ID if not present
        - Persists to repository
        - Returns enhanced signal
        """
        if not signal.id:
            import uuid
            signal.id = str(uuid.uuid4())
        
        signal.status = SignalStatus.GENERATED
        signal.generated_at = datetime.now()
        
        self.repo.save(signal)
        
        self.logger.info(
            f"📝 Signal registered: {signal.id[:8]}... "
            f"{signal.signal_type.value.upper()} @ ${signal.price:,.2f}"
        )
        
        return signal
    
    def mark_pending(self, signal_id: str) -> Optional[TradingSignal]:
        """Mark signal as pending (shown to user)."""
        signal = self.repo.get_by_id(signal_id)
        if signal and signal.is_actionable:
            signal.mark_pending()
            self.repo.update(signal)
            self.logger.info(f"⏳ Signal {signal_id[:8]}... → PENDING")
            return signal
        return None
    
    def mark_executed(
        self, 
        signal_id: str, 
        order_id: str
    ) -> Optional[TradingSignal]:
        """Mark signal as executed and link to order."""
        signal = self.repo.get_by_id(signal_id)
        if signal and signal.is_actionable:
            signal.mark_executed(order_id)
            self.repo.update(signal)
            self.logger.info(
                f"✅ Signal {signal_id[:8]}... → EXECUTED "
                f"(order: {order_id[:8]}..., latency: {signal.execution_latency_ms:.0f}ms)"
            )
            return signal
        return None
    
    def expire_stale_signals(self) -> int:
        """Expire signals older than TTL. Returns count expired."""
        count = self.repo.expire_old_pending(self.ttl_seconds)
        if count > 0:
            self.logger.info(f"⏰ Expired {count} stale signals")
        return count
    
    def get_signal_for_order(self, order_id: str) -> Optional[TradingSignal]:
        """Get the signal that created an order."""
        return self.repo.get_by_order_id(order_id)
    
    def get_pending_signals(self) -> List[TradingSignal]:
        """Get all pending signals."""
        return self.repo.get_by_status(SignalStatus.PENDING)
    
    def get_signal_history(
        self,
        days: int = 7,
        limit: int = 100,
        offset: int = 0
    ) -> List[TradingSignal]:
        """Get signal history for the last N days."""
        start_date = datetime.now() - timedelta(days=days)
        return self.repo.get_history(
            start_date=start_date,
            limit=limit,
            offset=offset
        )
```

---

## 7. FRONTEND QUERY PATTERNS

### 7.1 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/signals/pending` | GET | Get pending signals |
| `/signals/history` | GET | Get signal history (paginated) |
| `/signals/{id}` | GET | Get signal by ID |
| `/signals/{id}/execute` | POST | Execute a pending signal |

### 7.2 WebSocket Events

```javascript
// Signal Events via WebSocket
{
  "type": "signal_generated",
  "payload": {
    "id": "uuid",
    "signal_type": "buy",
    "status": "generated",
    "price": 89500.00,
    "confidence": 0.78,
    // ... full signal data
  }
}

{
  "type": "signal_status_changed",
  "payload": {
    "id": "uuid",
    "old_status": "pending",
    "new_status": "executed",
    "order_id": "order-uuid"
  }
}
```

### 7.3 Signal History Panel Data

```json
{
  "signals": [
    {
      "id": "abc-123",
      "signal_type": "buy",
      "status": "executed",
      "price": 89500.00,
      "confidence": 0.78,
      "generated_at": "2025-12-23T10:00:00",
      "executed_at": "2025-12-23T10:00:02",
      "execution_latency_ms": 2150,
      "order_id": "order-456",
      "outcome": {
        "pnl": 125.50,
        "pnl_pct": 1.25,
        "exit_reason": "TP1"
      }
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 20
  }
}
```

---

## 8. IMPLEMENTATION CHECKLIST

### 8.1 Backend Tasks

| # | Task | File | Priority |
|---|------|------|----------|
| 1 | Create SignalStatus enum | `signal_status.py` | P0 |
| 2 | Enhance TradingSignal entity | `trading_signal.py` | P0 |
| 3 | Create ISignalRepository interface | `i_signal_repository.py` | P0 |
| 4 | Implement SQLiteSignalRepository | `sqlite_signal_repository.py` | P0 |
| 5 | Create SignalLifecycleService | `signal_lifecycle_service.py` | P0 |
| 6 | Integrate with SignalGenerator | `signal_generator.py` | P1 |
| 7 | Create API endpoints | `routers/signals.py` | P1 |
| 8 | Add WebSocket events | `websocket_manager.py` | P1 |

### 8.2 Frontend Tasks

| # | Task | Component | Priority |
|---|------|-----------|----------|
| 1 | Signal History Panel | `SignalHistoryPanel.tsx` | P1 |
| 2 | Pending Signals List | `PendingSignals.tsx` | P1 |
| 3 | Signal Detail Modal | `SignalDetailModal.tsx` | P2 |
| 4 | Execution Timeline | `ExecutionTimeline.tsx` | P2 |

---

## 9. DEPENDENCIES

### 9.1 Python Packages

```
# Already available - no new dependencies needed
```

### 9.2 Database

```
SQLite - using existing paper_trading.db
```

---

## 10. HANDOFF TO BACKEND

### 10.1 Files to Create

| File | Description |
|------|-------------|
| `src/domain/value_objects/signal_status.py` | SignalStatus enum |
| `src/domain/repositories/i_signal_repository.py` | Repository interface |
| `src/infrastructure/repositories/sqlite_signal_repository.py` | SQLite impl |
| `src/application/services/signal_lifecycle_service.py` | Lifecycle service |
| `src/api/routers/signals.py` | API endpoints |

### 10.2 Files to Modify

| File | Changes |
|------|---------|
| `src/domain/entities/trading_signal.py` | Add id, status, timestamps, order_id |
| `src/application/signals/signal_generator.py` | Register signals via lifecycle service |
| `src/api/dependencies.py` | Add signal lifecycle service DI |
| `src/api/websocket_manager.py` | Add signal status events |

---

**Spec Version:** 1.0  
**Author:** Quant Specialist AI  
**Handoff To:** Backend Engineer AI
