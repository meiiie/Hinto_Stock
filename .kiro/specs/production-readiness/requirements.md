# Requirements Document

## Introduction

Spec này giải quyết 3 vấn đề critical được chuyên gia chỉ ra trong phanhoi3.md để chuẩn bị cho Shadow Trading:
1. State Recovery - Khôi phục trạng thái khi restart để tránh "Vị thế mồ côi"
2. Real Spread Filter - Lấy bid/ask thực từ bookTicker thay vì estimate
3. DI Container Refactor - Inject dependencies đúng cách theo Clean Architecture

## Glossary

- **State_Recovery_System**: Hệ thống khôi phục trạng thái trading khi bot restart
- **BookTicker_Client**: Client lắng nghe best bid/ask từ Binance WebSocket
- **Orphaned_Position**: Vị thế bị "mồ côi" khi bot quên mất đang giữ lệnh
- **DI_Container**: Dependency Injection Container quản lý dependencies
- **Spread**: Chênh lệch giữa giá Ask và Bid, tính bằng (Ask-Bid)/Bid

## Requirements

### Requirement 1: State Recovery on Startup

**User Story:** As a trader, I want the bot to recover its previous state when restarting, so that open positions are not orphaned and continue to be managed.

#### Acceptance Criteria

1. WHEN the RealtimeService starts THEN the State_Recovery_System SHALL check the database for the last persisted state
2. WHEN the last state is IN_POSITION THEN the State_Recovery_System SHALL verify the position exists on Binance exchange
3. IF the position exists on exchange THEN the State_Recovery_System SHALL restore IN_POSITION state and skip warm-up
4. IF the position was closed while bot was offline THEN the State_Recovery_System SHALL transition to SCANNING state
5. WHEN recovery completes THEN the State_Recovery_System SHALL log the recovery action taken

### Requirement 2: Real-time Spread from BookTicker

**User Story:** As a trader, I want the spread filter to use real bid/ask prices, so that I avoid entering trades during high spread conditions.

#### Acceptance Criteria

1. WHEN the RealtimeService starts THEN the BookTicker_Client SHALL subscribe to the bookTicker WebSocket stream
2. WHEN a bookTicker message is received THEN the BookTicker_Client SHALL update current_bid and current_ask values
3. WHEN HardFilters checks spread THEN the HardFilters SHALL use real bid/ask from BookTicker_Client
4. IF bookTicker data is stale (older than 5 seconds) THEN the HardFilters SHALL block trading with reason "Stale spread data"
5. WHEN spread exceeds threshold THEN the HardFilters SHALL log the actual spread value and threshold

### Requirement 3: DI Container Integration

**User Story:** As a developer, I want all dependencies injected via DI Container, so that the code is testable and follows Clean Architecture.

#### Acceptance Criteria

1. WHEN DIContainer is initialized THEN the DIContainer SHALL provide TradingStateMachine instance
2. WHEN DIContainer is initialized THEN the DIContainer SHALL provide WarmupManager instance
3. WHEN DIContainer is initialized THEN the DIContainer SHALL provide HardFilters instance
4. WHEN DIContainer is initialized THEN the DIContainer SHALL provide BookTickerClient instance
5. WHEN RealtimeService is created THEN the RealtimeService SHALL receive all dependencies from DIContainer
