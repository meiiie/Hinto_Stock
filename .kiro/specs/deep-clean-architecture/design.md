# Design Document: Deep Clean Architecture Refactor

## Overview

Thực hiện deep refactor để đảm bảo toàn bộ codebase tuân thủ Clean Architecture. Mục tiêu là cải thiện từng component/page theo nguyên tắc SOLID và Clean Architecture, đảm bảo tính toàn vẹn kiến trúc.

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   API (FastAPI) │  │   Frontend (React/Tauri)        │   │
│  │   - Routers     │  │   - Components                  │   │
│  │   - WebSocket   │  │   - Hooks                       │   │
│  └────────┬────────┘  └────────────────┬────────────────┘   │
└───────────┼────────────────────────────┼────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │    Services     │  │    Use Cases    │  │    DTOs     │  │
│  │ - RealtimeServ  │  │ - FetchData     │  │ - Request   │  │
│  │ - PaperTrading  │  │ - Calculate     │  │ - Response  │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────┘  │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │    Entities     │  │  Repositories   │  │  Services   │  │
│  │ - Candle        │  │  (Interfaces)   │  │ (Domain     │  │
│  │ - Signal        │  │ - IOrderRepo    │  │  Logic)     │  │
│  │ - Position      │  │ - IMarketRepo   │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
            ▲                    ▲
            │                    │
┌───────────┴────────────────────┴────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Persistence   │  │   External API  │  │  Indicators │  │
│  │ - SQLiteRepo    │  │ - BinanceClient │  │ - TALib     │  │
│  │                 │  │ - WebSocket     │  │ - ATR/ADX   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Direction Rules

```
Domain ← Application ← Infrastructure
                    ← Presentation
```

- Domain: NO external dependencies
- Application: Only depends on Domain
- Infrastructure: Implements Domain interfaces
- Presentation: Calls Application services

## Components and Interfaces

### Backend Components to Refactor

| Component | Current Location | Issues | Target State |
|-----------|-----------------|--------|--------------|
| RealtimeService | application/services | Too many responsibilities | Split into smaller services |
| SignalGenerator | application/signals | Direct infrastructure deps | Use DI |
| API Routers | api/routers | Some direct infra imports | Only call Application |
| Calculators | application/services | Should be in Infrastructure | Move to infrastructure |

### Frontend Components to Refactor

| Component | Current Location | Issues | Target State |
|-----------|-----------------|--------|--------------|
| App.tsx | src/ | Contains business logic | Extract to hooks/services |
| CandleChart | components/ | Mixed concerns | Pure presentation |
| useMarketData | hooks/ | Good structure | Keep, enhance |

## Data Models

### Domain Entities (Pure)

```python
# domain/entities/candle.py - PURE, no external deps
@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

# domain/entities/trading_signal.py - PURE
@dataclass
class TradingSignal:
    signal_type: SignalType
    price: float
    confidence: float
    timestamp: datetime
```

### Application DTOs

```python
# application/dto/market_data_dto.py
@dataclass
class MarketDataResponse:
    candles: List[CandleDTO]
    indicators: IndicatorsDTO
    
# application/dto/signal_dto.py
@dataclass
class SignalDTO:
    type: str
    price: float
    confidence: float
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Domain Layer Independence
*For any* file in the domain/ directory, scanning its imports should reveal NO imports from infrastructure/ or presentation/ directories.
**Validates: Requirements 1.1**

### Property 2: Domain Repository Abstraction
*For any* repository file in domain/repositories/, it should contain only abstract base classes or Protocol definitions, with no concrete implementations.
**Validates: Requirements 1.3**

### Property 3: Application Layer Dependencies
*For any* file in application/, its imports should only reference domain/ layer or abstract interfaces, never concrete infrastructure implementations.
**Validates: Requirements 2.1**

### Property 4: Infrastructure Isolation - External APIs
*For any* file that imports external API libraries (requests, httpx, websockets), that file should be located in infrastructure/ directory.
**Validates: Requirements 3.2**

### Property 5: Infrastructure Isolation - Database
*For any* file that imports database libraries (sqlite3, sqlalchemy), that file should be located in infrastructure/ directory.
**Validates: Requirements 3.3**

### Property 6: Presentation Layer Dependencies
*For any* API router file in api/routers/, its imports should only reference application/ layer services, not infrastructure/ directly.
**Validates: Requirements 4.1**

### Property 7: Frontend State Separation
*For any* React component file in components/, API calls (fetch, axios) should NOT appear directly; they should be in hooks/ or services/.
**Validates: Requirements 5.2, 5.3**

### Property 8: Dependency Injection Consistency
*For any* service class in application/services/, dependencies should be received via constructor parameters, not instantiated internally.
**Validates: Requirements 6.1**

### Property 9: Import Direction Compliance
*For any* Python file in the codebase, imports should follow the dependency direction: Domain ← Application ← Infrastructure/Presentation. No reverse imports allowed.
**Validates: Requirements 7.3**

## Error Handling

- Architectural violations should be caught by static analysis
- Property tests should fail fast on violations
- Clear error messages indicating which rule was violated

## Testing Strategy

### Dual Testing Approach

**Unit Tests:**
- Test individual components in isolation
- Mock dependencies for Application layer tests
- Test Domain entities without any mocks

**Property-Based Tests:**
- Use `hypothesis` library for Python
- Scan codebase files and verify architectural properties
- Run on every CI build to prevent regressions

### Property Test Implementation

```python
# tests/property/test_architecture_properties.py
from hypothesis import given, strategies as st
import ast
import os

def get_python_files(directory: str) -> List[str]:
    """Get all Python files in directory recursively."""
    ...

def get_imports(filepath: str) -> List[str]:
    """Extract all imports from a Python file using AST."""
    ...

class TestArchitectureProperties:
    """Property tests for Clean Architecture compliance."""
    
    def test_domain_layer_independence(self):
        """Property 1: Domain has no infra/presentation imports."""
        domain_files = get_python_files('src/domain')
        for filepath in domain_files:
            imports = get_imports(filepath)
            for imp in imports:
                assert 'infrastructure' not in imp
                assert 'presentation' not in imp
                assert 'api' not in imp
```
