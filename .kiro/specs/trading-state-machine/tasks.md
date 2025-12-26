# Implementation Plan

- [x] 1. Create SystemState enum and state machine foundation


  - [x] 1.1 Create SystemState enum in `src/domain/state_machine.py`



    - Define 6 states: BOOTSTRAP, SCANNING, ENTRY_PENDING, IN_POSITION, COOLDOWN, HALTED
    - Add helper methods for state validation
    - _Requirements: 2.1_
  - [x]* 1.2 Write property test for state enum completeness




    - **Property: SystemState enum has exactly 6 states**


    - **Validates: Requirements 2.1**
  - [x] 1.3 Create StateTransition and PersistedState data models

    - Define dataclasses in `src/domain/entities/state_models.py`
    - _Requirements: 2.8, 5.1_

- [x] 2. Implement TradingStateMachine core
  - [x] 2.1 Create TradingStateMachine class in `src/application/services/trading_state_machine.py`
    - Initialize with EventBus, state repository, and config
    - Implement state property and transition validation
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [x] 2.2 Implement state transition methods
    - `transition_to(new_state, reason)` with validation
    - Publish state change events via EventBus





    - _Requirements: 2.8_


  - [ ]* 2.3 Write property test for state transition validity
    - **Property 4: State Transition Validity**

    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6**
  - [ ]* 2.4 Write property test for HALTED reachability
    - **Property 5: HALTED Reachability**
    - **Validates: Requirements 2.7**
  - [ ]* 2.5 Write property test for state change event publishing
    - **Property 6: State Change Event Publishing**
    - **Validates: Requirements 2.8**

- [x] 3. Checkpoint - Ensure all tests pass
  - ✅ Tests passed






- [x] 4. Implement WarmupManager for cold start


  - [x] 4.1 Create WarmupManager class in `src/application/services/warmup_manager.py`
    - Load historical candles from REST API
    - Process candles through indicators without triggering signals
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 4.2 Implement VWAP daily reset logic
    - Detect 00:00 UTC boundary crossing
    - Reset VWAP accumulated values
    - _Requirements: 1.4_


  - [x]* 4.3 Write property test for bootstrap signal suppression


    - **Property 1: Bootstrap Signal Suppression**


    - **Validates: Requirements 1.2**
  - [ ]* 4.4 Write property test for warm-up state transition
    - **Property 2: Warm-up State Transition**
    - **Validates: Requirements 1.1, 1.3**

  - [ ]* 4.5 Write property test for VWAP daily reset
    - **Property 3: VWAP Daily Reset**
    - **Validates: Requirements 1.4**

- [x] 5. Checkpoint - Ensure all tests pass
  - ✅ Tests passed

- [x] 6. Implement HardFilters
  - [x] 6.1 Create HardFilters class in `src/application/services/hard_filters.py`
    - Implement ADX filter with configurable threshold (default 25)
    - Implement Spread filter with configurable threshold (default 0.1%)
    - Return FilterResult with pass/fail and reason
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4_
  - [ ]* 6.2 Write property test for ADX filter enforcement
    - **Property 7: ADX Filter Enforcement**
    - **Validates: Requirements 3.1, 3.2**
  - [ ]* 6.3 Write property test for spread filter enforcement
    - **Property 8: Spread Filter Enforcement**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 7. Implement State Persistence
  - [x] 7.1 Create IStateRepository interface in `src/domain/repositories/i_state_repository.py`
    - Define save_state and load_state abstract methods
    - _Requirements: 5.1, 5.2_
  - [x] 7.2 Create SQLiteStateRepository in `src/infrastructure/persistence/sqlite_state_repository.py`
    - Implement state persistence to SQLite
    - Handle position verification on restart
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 7.3 Write property test for state persistence round-trip
    - **Property 9: State Persistence Round-Trip**
    - **Validates: Requirements 5.1, 5.2**

- [x] 8. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement Cooldown logic
  - [x] 9.1 Add cooldown counter and logic to TradingStateMachine
    - Track candles in COOLDOWN state
    - Transition to SCANNING after cooldown_candles (default 4)
    - _Requirements: 2.6_
  - [ ]* 9.2 Write property test for cooldown duration
    - **Property 10: Cooldown Duration**
    - **Validates: Requirements 2.6**

- [x] 10. Integrate with RealtimeService
  - [x] 10.1 Update RealtimeService to use TradingStateMachine
    - Inject TradingStateMachine dependency
    - Call state machine on candle received
    - Use WarmupManager in start() method
    - _Requirements: 1.1, 1.2, 1.3, 2.2, 2.3, 2.4, 2.5_
  - [x] 10.2 Update RealtimeService to use HardFilters
    - Check ADX filter before signal generation
    - Check Spread filter before order placement
    - _Requirements: 3.1, 4.1_
  - [x] 10.3 Handle error transitions to HALTED state
    - Catch critical errors and transition to HALTED
    - Log error details
    - _Requirements: 1.5, 2.7_

- [x] 11. Update EventBus for state events
  - [x] 11.1 Add state change event type to EventBus
    - Add STATE_CHANGE to EventType enum
    - Add publish_state_change method
    - _Requirements: 2.8_

- [x] 12. Final Checkpoint - Ensure all tests pass
  - ✅ All 291 tests passed (76.40s)
