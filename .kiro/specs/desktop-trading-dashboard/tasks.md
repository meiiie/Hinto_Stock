# Implementation Plan

## Desktop Trading Dashboard - Hinto Trader Pro

- [x] 1. Setup Backend API Foundation




  - [x] 1.1 Create Paper Trading Service with SQLite persistence



    - Implement `PaperTradingService` class with trade execution, position management
    - Create SQLite tables for `paper_trades` and `settings`





    - Implement `execute_trade()`, `close_position()`, `get_portfolio()` methods
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 1.2 Write property test for trade persistence round-trip

    - **Property 2: Paper Trade Persistence Round-Trip**
    - **Validates: Requirements 4.3**
  - [x] 1.3 Create Settings API endpoint


    - Implement `POST /settings` endpoint for risk_percent, rr_ratio
    - Persist settings to SQLite and apply to signal generator


    - _Requirements: 6.3_
  - [x] 1.4 Write property test for settings persistence

    - **Property 6: Settings Persistence and Application**
    - **Validates: Requirements 6.3**



- [x] 2. Implement WebSocket Streaming


  - [x] 2.1 Create WebSocket Manager with Pub/Sub pattern

    - Implement connection tracking with graceful disconnect handling
    - Create broadcast mechanism from Trading Engine to connected clients
    - Handle `WebSocketDisconnect` exception without crashing
    - _Requirements: 5.2, 5.3_
  - [x] 2.2 Write property test for engine stability under connection churn














    - **Property 4: Trading Engine Stability Under Connection Churn**







    - **Validates: Requirements 5.2**
  - [x] 2.3 Create WebSocket endpoint `/ws/stream/{symbol}`









    - Stream real-time candle data with indicators (VWAP, BB, StochRSI)








    - Include signal notifications in stream








    - _Requirements: 1.1, 1.2_





- [ ] 3. Implement Historical Data API
  - [x] 3.1 Create `/ws/history/{symbol}` endpoint


    - Return candles with pre-calculated VWAP and Bollinger Bands


    - Support timeframe parameter (1m, 15m, 1h)




    - _Requirements: 5.4, 2.1_
  - [x] 3.2 Write property test for API response completeness

    - **Property 5: Historical Data API Response Completeness**

    - **Validates: Requirements 5.4**



- [x] 4. Checkpoint - Backend API Complete




  - Ensure all tests pass, ask the user if questions arise.



- [ ] 5. Implement Trade History and Performance
  - [x] 5.1 Create paginated trade history endpoint




    - Implement `GET /trades/history?page=N&limit=L`
    - Return trades sorted by entry_time descending
    - _Requirements: 7.1, 7.2_




  - [x] 5.2 Write property test for pagination correctness



    - **Property 7: Trade History Pagination Correctness**
    - **Validates: Requirements 7.1**
  - [ ] 5.3 Implement performance metrics calculator
    - Calculate win_rate, profit_factor, max_drawdown, total_pnl
    - Create `GET /trades/performance` endpoint
    - _Requirements: 7.3_
  - [ ] 5.4 Write property test for performance metrics
    - **Property 8: Performance Metrics Calculation**
    - **Validates: Requirements 7.3**

- [ ] 6. Implement PnL Calculator
  - [ ] 6.1 Create unrealized PnL calculation in PaperTradingService
    - Implement formula: LONG = (current - entry) * size, SHORT = (entry - current) * size
    - Update PnL on every market data tick
    - _Requirements: 4.4_
  - [ ] 6.2 Write property test for PnL calculation
    - **Property 3: Unrealized PnL Calculation**
    - **Validates: Requirements 4.4**

- [ ] 7. Checkpoint - Backend Complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Frontend Chart Implementation
  - [ ] 8.1 Enhance CandleChart with signal markers
    - Add green upward arrow for BUY signals
    - Add red downward arrow for SELL signals
    - Display entry/SL/TP horizontal lines
    - _Requirements: 3.1, 3.2, 3.3_
  - [ ] 8.2 Implement Client-Side Candle Aggregator
    - Create aggregation logic for 1m → 15m/1h
    - Use formula: `floor(time / intervalSeconds) * intervalSeconds`
    - Update High/Low/Close on each 1m update
    - _Requirements: 2.5_
  - [ ] 8.3 Write property test for candle aggregation (TypeScript/fast-check)
    - **Property 1: Client-Side Candle Aggregation Correctness**
    - **Validates: Requirements 2.5**
  - [ ] 8.4 Add loading spinner for timeframe switching
    - Show "Loading..." overlay during data fetch
    - Clear current candle ref on timeframe change
    - _Requirements: 2.2_

- [ ] 9. Frontend Portfolio Panel
  - [ ] 9.1 Create Portfolio component
    - Display virtual balance, equity, unrealized PnL
    - Show list of open positions with real-time PnL
    - _Requirements: 4.1, 4.4_
  - [ ] 9.2 Create Trade History component
    - Display paginated trade history with all required fields
    - Show date, symbol, direction, entry/exit prices, PnL, duration
    - _Requirements: 7.2_
  - [ ] 9.3 Create Performance Dashboard component
    - Display win rate, profit factor, max drawdown, total PnL
    - Load last 7 days of data on startup
    - _Requirements: 7.3, 7.4_

- [ ] 10. Frontend Connection Management
  - [ ] 10.1 Implement WebSocket reconnection logic
    - Auto-reconnect every 5 seconds on disconnect
    - Display "Disconnected" / "Reconnecting..." status
    - _Requirements: 1.3, 1.4_
  - [ ] 10.2 Create ConnectionStatus component
    - Show Online/Offline indicator
    - Display service name, version from /system/status
    - _Requirements: 6.1, 6.2_

- [ ] 11. Frontend Settings Panel
  - [ ] 11.1 Create Settings component
    - Allow editing Risk %, R:R ratio
    - Display current strategy parameters (VWAP, BB, StochRSI settings)
    - Call POST /settings on save
    - _Requirements: 6.3, 6.4_

- [ ] 12. Signal Tooltip Implementation
  - [ ] 12.1 Add tooltip to signal markers
    - Display confidence, R:R ratio, timestamp on hover
    - _Requirements: 3.4_

- [ ] 13. Final Checkpoint - Full Integration
  - Ensure all tests pass, ask the user if questions arise.
