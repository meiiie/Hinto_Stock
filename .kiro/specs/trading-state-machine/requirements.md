# Requirements Document

## Introduction

Hệ thống Trading State Machine là "bộ não" của Bot giao dịch Hinto Stock. Tính năng này quản lý vòng đời giao dịch thông qua Finite State Machine (FSM), đảm bảo dữ liệu indicator chính xác ngay từ khi khởi động (Cold Start Warm-up), và lọc nhiễu thị trường bằng các Hard Filters (ADX, Spread) theo tư duy Game Theory.

## Glossary

- **FSM (Finite State Machine)**: Máy trạng thái hữu hạn - mô hình quản lý các trạng thái và chuyển đổi giữa chúng
- **Cold Start**: Trạng thái khi bot mới khởi động, chưa có đủ dữ liệu lịch sử
- **Warm-up**: Quá trình nạp dữ liệu lịch sử để các indicator có giá trị chính xác
- **VWAP**: Volume Weighted Average Price - Giá trung bình theo khối lượng, reset mỗi ngày 00:00 UTC
- **StochRSI**: Stochastic RSI - Indicator đo momentum
- **ADX**: Average Directional Index - Đo sức mạnh xu hướng
- **Spread**: Chênh lệch giữa giá Ask và Bid
- **Cooldown**: Thời gian nghỉ sau khi đóng lệnh để tránh overtrading
- **Hard Filter**: Bộ lọc cứng - điều kiện bắt buộc phải thỏa mãn trước khi vào lệnh
- **Trailing Stop**: Stop loss di động theo giá

## Requirements

### Requirement 1: Cold Start & Data Warm-up

**User Story:** As a trader, I want the bot to load historical data before starting live trading, so that indicators like VWAP and StochRSI have accurate values from the first candle.

#### Acceptance Criteria

1. WHEN the system starts THEN the RealtimeService SHALL transition to BOOTSTRAP state and load at least 1000 historical 15-minute candles
2. WHILE in BOOTSTRAP state THE system SHALL process historical candles through indicator calculators without triggering any trading signals
3. WHEN historical data processing completes THEN the system SHALL log the current VWAP value and transition to SCANNING state
4. WHEN a new day begins at 00:00 UTC THEN the VWAP calculator SHALL automatically reset its accumulated values
5. IF historical data loading fails THEN the system SHALL transition to HALTED state and log the error

### Requirement 2: Finite State Machine (FSM)

**User Story:** As a trader, I want the bot to manage trading lifecycle through defined states, so that orders are placed and managed in a controlled, predictable manner.

#### Acceptance Criteria

1. THE SystemState enum SHALL define exactly six states: BOOTSTRAP, SCANNING, ENTRY_PENDING, IN_POSITION, COOLDOWN, and HALTED
2. WHEN in SCANNING state and a valid signal is generated THEN the system SHALL place a limit entry order and transition to ENTRY_PENDING state
3. WHEN in ENTRY_PENDING state and the order is filled THEN the system SHALL transition to IN_POSITION state and place a hard stop-loss order
4. WHEN in ENTRY_PENDING state and the order is canceled or expired THEN the system SHALL transition back to SCANNING state
5. WHEN in IN_POSITION state and exit conditions are met THEN the system SHALL close the position and transition to COOLDOWN state
6. WHILE in COOLDOWN state THE system SHALL wait for a configurable number of candles (default 4) before transitioning to SCANNING state
7. WHEN a critical error occurs or panic button is pressed THEN the system SHALL transition to HALTED state from any state
8. WHEN state transitions occur THEN the system SHALL publish state change events via EventBus

### Requirement 3: ADX Hard Filter

**User Story:** As a trader, I want the bot to avoid trading in sideways markets, so that the trend pullback strategy does not get stopped out repeatedly.

#### Acceptance Criteria

1. WHEN in SCANNING state and ADX(14) value is below 25 THEN the system SHALL skip signal generation and remain in SCANNING state
2. WHEN ADX filter blocks a potential trade THEN the system SHALL log the ADX value and reason for skipping
3. THE ADX threshold value SHALL be configurable with a default of 25

### Requirement 4: Spread Hard Filter

**User Story:** As a trader, I want the bot to avoid trading when spread is too wide, so that entry costs do not erode potential profits.

#### Acceptance Criteria

1. WHEN placing an entry order THE system SHALL first check the current bid-ask spread percentage
2. IF spread percentage exceeds the threshold (default 0.1%) THEN the system SHALL cancel the entry and remain in SCANNING state
3. WHEN spread filter blocks a trade THEN the system SHALL log the spread value and reason for skipping
4. THE spread threshold SHALL be configurable with a default of 0.1%

### Requirement 5: State Persistence and Recovery

**User Story:** As a trader, I want the bot to remember its state after restart, so that open positions are not orphaned.

#### Acceptance Criteria

1. WHEN state transitions occur THEN the system SHALL persist the current state and relevant order IDs to storage
2. WHEN the system restarts with an existing persisted state THEN the system SHALL restore to that state after warm-up
3. IF the persisted state is IN_POSITION THEN the system SHALL verify the position still exists on the exchange before resuming
