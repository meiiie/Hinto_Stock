# Implementation Plan

- [x] 1. Create BookTickerClient for real bid/ask data





  - [x] 1.1 Create IBookTickerClient interface in `src/domain/interfaces/`


    - Define subscribe, get_best_bid_ask, is_data_fresh methods
    - _Requirements: 2.1, 2.2_
  - [ ] 1.2 Create BinanceBookTickerClient in `src/infrastructure/websocket/`
    - Implement WebSocket subscription to bookTicker stream
    - Parse bookTicker messages and update bid/ask










    - Track timestamp for freshness check
    - _Requirements: 2.1, 2.2, 2.4_
  - [x]* 1.3 Write property test for bookTicker data freshness








    - **Property 2: BookTicker Data Freshness**


    - **Validates: Requirements 2.2, 2.4**

- [x] 2. Update HardFilters to use real spread data


  - [ ] 2.1 Add BookTickerClient dependency to HardFilters
    - Inject via constructor
    - Add check_spread_filter_realtime() method
    - _Requirements: 2.3_




  - [ ] 2.2 Update RealtimeService to use realtime spread check
    - Replace estimated spread with real bid/ask
    - Handle stale data case
    - _Requirements: 2.3, 2.4, 2.5_
  - [ ]* 2.3 Write property test for spread filter using real data
    - **Property 3: Spread Filter Uses Real Data**
    - **Validates: Requirements 2.3**

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement State Recovery System
  - [ ] 4.1 Create RecoveryResult dataclass in `src/domain/entities/state_models.py`
    - Define action, previous_state, current_state, position_verified, message
    - _Requirements: 1.5_
  - [ ] 4.2 Create StateRecoveryService in `src/application/services/`
    - Implement recover_state() method
    - Check database for last state
    - Verify position with exchange if IN_POSITION
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [ ] 4.3 Integrate StateRecoveryService into RealtimeService.start()
    - Call recovery before warm-up
    - Skip warm-up if restored to IN_POSITION
    - _Requirements: 1.3, 1.4_
  - [ ]* 4.4 Write property test for state recovery correctness
    - **Property 1: State Recovery Correctness**
    - **Validates: Requirements 1.2, 1.3, 1.4**

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Refactor DI Container

  - [x] 6.1 Add BookTickerClient to DIContainer

    - Create get_book_ticker_client() method
    - _Requirements: 3.4_

  - [ ] 6.2 Add TradingStateMachine to DIContainer
    - Create get_trading_state_machine() method

    - _Requirements: 3.1_
  - [x] 6.3 Add WarmupManager to DIContainer

    - Create get_warmup_manager() method
    - _Requirements: 3.2_

  - [ ] 6.4 Add HardFilters to DIContainer
    - Create get_hard_filters() method with BookTickerClient injection

    - _Requirements: 3.3_
  - [ ] 6.5 Add StateRecoveryService to DIContainer
    - Create get_state_recovery_service() method
    - _Requirements: 3.5_
  - [ ] 6.6 Update get_realtime_service() to use all dependencies
    - Inject all new dependencies from container
    - _Requirements: 3.5_

- [x] 7. Update API dependencies


  - [x] 7.1 Update `src/api/dependencies.py` to use DIContainer

    - Create RealtimeService via container
    - _Requirements: 3.5_

- [x] 8. Final Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.
