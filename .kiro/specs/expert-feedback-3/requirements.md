# Requirements Document

## Introduction

Tài liệu này mô tả các yêu cầu để hoàn thiện Backend theo phản hồi từ chuyên gia (phanhoi3.md). Mục tiêu là đạt "Production Ready Architecture" trước khi bắt đầu Shadow Trading. Ba cải tiến chính bao gồm: Exchange Service Abstraction, Configuration Management, và Safety Enhancements cho HALTED state.

## Glossary

- **Trading_System**: Hệ thống giao dịch tự động BTC/USDT
- **IExchangeService**: Interface trừu tượng cho các thao tác exchange (paper/real)
- **PaperExchangeService**: Implementation giả lập exchange cho paper trading
- **BinanceExchangeService**: Implementation thực cho Binance exchange
- **StateRecoveryService**: Service phục hồi trạng thái khi khởi động lại
- **HALTED**: Trạng thái dừng khẩn cấp, yêu cầu can thiệp thủ công
- **BookTicker**: Dữ liệu bid/ask realtime từ Binance
- **Position**: Vị thế giao dịch đang mở (LONG/SHORT)
- **MAX_BOOK_TICKER_AGE_SECONDS**: Ngưỡng thời gian tối đa cho dữ liệu BookTicker còn hợp lệ

## Requirements

### Requirement 1: Exchange Service Abstraction

**User Story:** As a system architect, I want to separate paper trading from real exchange operations, so that the system can easily switch between paper and live trading modes without code changes.

#### Acceptance Criteria

1. WHEN the Trading_System initializes THEN the Trading_System SHALL load IExchangeService interface from domain layer
2. WHEN TRADING_MODE is set to "PAPER" THEN the DIContainer SHALL instantiate PaperExchangeService
3. WHEN TRADING_MODE is set to "REAL" THEN the DIContainer SHALL instantiate BinanceExchangeService
4. WHEN StateRecoveryService calls get_position() THEN the IExchangeService SHALL return Position data regardless of trading mode
5. WHEN PaperExchangeService receives get_position() request THEN the PaperExchangeService SHALL query local database for open positions
6. WHEN BinanceExchangeService receives get_position() request THEN the BinanceExchangeService SHALL call Binance API for real positions

### Requirement 2: Configuration Management

**User Story:** As a system operator, I want configurable timeouts and thresholds, so that I can tune system behavior without code changes.

#### Acceptance Criteria

1. WHEN the Trading_System starts THEN the Trading_System SHALL load MAX_BOOK_TICKER_AGE_SECONDS from environment config
2. WHEN MAX_BOOK_TICKER_AGE_SECONDS is not set THEN the Trading_System SHALL use default value of 2.0 seconds
3. WHEN BookTickerClient checks data freshness THEN the BookTickerClient SHALL compare data age against MAX_BOOK_TICKER_AGE_SECONDS config value
4. IF MAX_BOOK_TICKER_AGE_SECONDS is set to non-positive value THEN the Trading_System SHALL reject the configuration and use default value

### Requirement 3: HALTED State Safety

**User Story:** As a system operator, I want enhanced safety checks for HALTED state, so that the system never auto-resumes from critical errors without manual intervention.

#### Acceptance Criteria

1. WHEN StateRecoveryService recovers state AND persisted state is HALTED THEN the StateRecoveryService SHALL keep the system in HALTED state
2. WHEN system recovers to HALTED state THEN the StateRecoveryService SHALL log warning message "Bot bị tắt khi đang HALTED. Giữ nguyên trạng thái dừng."
3. WHEN system recovers to HALTED state THEN the StateRecoveryService SHALL publish status event with reason "Recovered from HALTED state. Manual intervention required."
4. WHILE system is in HALTED state THEN the Trading_System SHALL prevent all trading operations
5. WHEN operator manually resumes from HALTED THEN the Trading_System SHALL transition to BOOTSTRAP state
