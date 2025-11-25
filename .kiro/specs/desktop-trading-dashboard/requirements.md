# Requirements Document

## Introduction

Hệ thống **Hinto Trader Pro Desktop** là ứng dụng desktop native cho trading cryptocurrency, chuyển đổi từ Streamlit Dashboard sang Tauri + React. Mục tiêu là xây dựng giao diện chuyên nghiệp như Binance Desktop với hiệu năng cao (60fps), hỗ trợ paper trading 7 ngày trước khi trade thật.

**Chiến lược giao dịch:** Trend Pullback (VWAP + Bollinger Bands + StochRSI) trên khung 15m/1h.

**Kiến trúc:** Client-Server Local với FastAPI backend và Tauri/React frontend.

## Glossary

- **Desktop_App**: Ứng dụng Tauri đóng gói React frontend thành native app (.exe)
- **Trading_Engine**: Python backend service xử lý logic trading và kết nối Binance
- **FastAPI_Server**: REST API server làm middleware giữa Trading Engine và Desktop App
- **VWAP**: Volume Weighted Average Price - chỉ báo xác định xu hướng chính
- **Bollinger_Bands**: Chỉ báo đo biến động, xác định vùng quá mua/bán
- **StochRSI**: Stochastic RSI - tín hiệu vào lệnh chính xác
- **Paper_Trading**: Giao dịch mô phỏng với tiền ảo để test chiến lược
- **Candle_Chart**: Biểu đồ nến hiển thị OHLCV data
- **WebSocket_Stream**: Kết nối real-time để nhận giá từ backend
- **Client_Side_Aggregation**: Logic frontend tổng hợp nến 1m thành 15m/1h

## Requirements

### Requirement 1: Real-time Price Display

**User Story:** As a trader, I want to see real-time BTC price updates, so that I can monitor market movements instantly.

#### Acceptance Criteria

1. WHEN the Desktop_App connects to FastAPI_Server via WebSocket THEN the Desktop_App SHALL display current BTC price within 1 second of connection
2. WHEN a new price update arrives from WebSocket_Stream THEN the Desktop_App SHALL update the price display within 100 milliseconds
3. WHEN the WebSocket connection is lost THEN the Desktop_App SHALL display a "Disconnected" status indicator and attempt reconnection every 5 seconds
4. WHEN the WebSocket reconnects successfully THEN the Desktop_App SHALL restore the "Connected" status and resume price updates

### Requirement 2: Interactive Candlestick Chart

**User Story:** As a trader, I want to view candlestick charts with strategy indicators, so that I can analyze market conditions and validate signals.

#### Acceptance Criteria

1. WHEN the Desktop_App loads THEN the Candle_Chart SHALL display 15-minute timeframe by default with at least 100 historical candles
2. WHEN a user selects a different timeframe (15m or 1h) THEN the Candle_Chart SHALL reload data for that timeframe and display a loading indicator during transition
3. WHEN displaying candles THEN the Candle_Chart SHALL render VWAP as an orange line (linewidth: 2) overlaid on the chart
4. WHEN displaying candles THEN the Candle_Chart SHALL render Bollinger_Bands as cyan lines (upper/lower, linewidth: 1, opacity: 0.5)
5. WHEN a 1-minute candle update arrives THEN the Desktop_App SHALL use Client_Side_Aggregation to update the current forming 15m/1h candle (High/Low/Close)
6. WHEN rendering chart layers THEN the Candle_Chart SHALL display candlesticks on top of indicator lines (correct Z-index priority)

### Requirement 3: Trading Signal Visualization

**User Story:** As a trader, I want to see buy/sell signals marked on the chart, so that I can understand when the system recommends entering or exiting positions.

#### Acceptance Criteria

1. WHEN a BUY signal is generated THEN the Candle_Chart SHALL display a green upward arrow marker at the signal candle
2. WHEN a SELL signal is generated THEN the Candle_Chart SHALL display a red downward arrow marker at the signal candle
3. WHEN displaying signal markers THEN the Desktop_App SHALL show entry price, stop-loss, and take-profit levels as horizontal lines
4. WHEN a user hovers over a signal marker THEN the Desktop_App SHALL display a tooltip with signal details (confidence, R:R ratio, timestamp)

### Requirement 4: Paper Trading Portfolio

**User Story:** As a trader, I want to execute paper trades and track my virtual portfolio, so that I can validate the strategy before using real money.

#### Acceptance Criteria

1. WHEN the Desktop_App starts THEN the Paper_Trading module SHALL display current virtual balance, equity, and open positions
2. WHEN a trading signal is generated THEN the Paper_Trading module SHALL allow manual execution or auto-execution based on user settings
3. WHEN a paper trade is executed THEN the Trading_Engine SHALL record the trade in SQLite database with timestamp, entry price, size, and signal metadata
4. WHEN displaying portfolio THEN the Desktop_App SHALL show unrealized PnL for open positions updated in real-time
5. WHEN a paper position is closed THEN the Desktop_App SHALL update realized PnL and trade history

### Requirement 5: Backend API Stability

**User Story:** As a system operator, I want the backend to remain stable regardless of frontend connections, so that trading logic continues uninterrupted.

#### Acceptance Criteria

1. WHEN FastAPI_Server starts THEN the Trading_Engine SHALL initialize as a background task without blocking API startup
2. WHEN multiple WebSocket clients connect and disconnect THEN the Trading_Engine SHALL continue running without interruption
3. WHEN a WebSocket client disconnects abruptly THEN the FastAPI_Server SHALL handle the disconnection gracefully without crashing
4. WHEN the Desktop_App requests historical data THEN the FastAPI_Server SHALL return candle data with pre-calculated VWAP and Bollinger_Bands values

### Requirement 6: System Status and Configuration

**User Story:** As a trader, I want to view system status and configure trading parameters, so that I can ensure the system is running correctly and adjust risk settings.

#### Acceptance Criteria

1. WHEN the Desktop_App loads THEN the system status panel SHALL display backend connection status (Online/Offline)
2. WHEN the backend is online THEN the status panel SHALL display service name, version, and current PnL
3. WHEN a user updates trading parameters (Risk %, R:R ratio) THEN the FastAPI_Server SHALL persist the settings and apply them to subsequent signals
4. WHEN displaying configuration THEN the Desktop_App SHALL show current strategy parameters (VWAP period, BB settings, StochRSI settings)

### Requirement 7: Data Persistence and History

**User Story:** As a trader, I want to view my trading history and performance metrics, so that I can analyze my results over time.

#### Acceptance Criteria

1. WHEN requesting trade history THEN the FastAPI_Server SHALL return paginated results from SQLite database
2. WHEN displaying history THEN the Desktop_App SHALL show trade date, symbol, direction, entry/exit prices, PnL, and duration
3. WHEN calculating performance THEN the Desktop_App SHALL display win rate, profit factor, max drawdown, and total PnL
4. WHEN the Desktop_App starts THEN the system SHALL load the last 7 days of paper trading data for analysis
