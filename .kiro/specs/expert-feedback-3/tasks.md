# Implementation Plan

- [x] 1. Create IExchangeService interface and data models


  - [x] 1.1 Create Position and OrderStatus dataclasses in domain layer



    - Create `src/domain/entities/exchange_models.py` with Position and OrderStatus


    - Add proper type hints and docstrings
    - _Requirements: 1.1, 1.4_
  - [ ] 1.2 Create IExchangeService interface
    - Create `src/domain/interfaces/i_exchange_service.py`
    - Define get_position(), get_order_status(), get_exchange_type() methods


    - Export from `src/domain/interfaces/__init__.py`


    - _Requirements: 1.1_
  - [ ]* 1.3 Write property test for Position return type consistency
    - **Property 2: Position Return Type Consistency**
    - **Validates: Requirements 1.4**


- [ ] 2. Enhance Config with new sections
  - [ ] 2.1 Add BookTickerConfig and SafetyConfig dataclasses
    - Add to `src/config.py`
    - BookTickerConfig with max_age_seconds (default 2.0)


    - SafetyConfig with allow_auto_resume_from_halted (default False)


    - Add TRADING_MODE config
    - _Requirements: 2.1, 2.2_
  - [ ] 2.2 Add config validation
    - Validate max_age_seconds is positive
    - Use default if invalid
    - _Requirements: 2.4_
  - [x]* 2.3 Write property test for config validation


    - **Property 4: Config Validation for Non-Positive Values**


    - **Validates: Requirements 2.4**

- [ ] 3. Implement PaperExchangeService
  - [ ] 3.1 Create PaperExchangeService class
    - Create `src/infrastructure/exchange/paper_exchange_service.py`
    - Implement IExchangeService interface
    - Use IOrderRepository for database queries

    - Calculate positions from order history


    - _Requirements: 1.2, 1.5_
  - [ ]* 3.2 Write unit tests for PaperExchangeService
    - Test get_position() returns correct Position
    - Test get_exchange_type() returns "paper"
    - _Requirements: 1.5_


- [ ] 4. Implement BinanceExchangeService
  - [ ] 4.1 Create BinanceExchangeService class
    - Create `src/infrastructure/exchange/binance_exchange_service.py`
    - Implement IExchangeService interface
    - Use BinanceRestClient for API calls
    - Handle API errors gracefully
    - _Requirements: 1.3, 1.6_
  - [ ]* 4.2 Write unit tests for BinanceExchangeService
    - Test get_position() with mocked API
    - Test get_exchange_type() returns "binance"
    - _Requirements: 1.6_

- [ ] 5. Update DIContainer with exchange service factory
  - [ ] 5.1 Add get_exchange_service() factory method
    - Return PaperExchangeService when TRADING_MODE="PAPER"
    - Return BinanceExchangeService when TRADING_MODE="REAL"
    - Use singleton pattern
    - _Requirements: 1.2, 1.3_
  - [ ]* 5.2 Write property test for exchange service factory
    - **Property 1: Exchange Service Factory Correctness**
    - **Validates: Requirements 1.2, 1.3**

- [x] 6. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Update StateRecoveryService with HALTED safety

  - [x] 7.1 Update constructor to use IExchangeService


    - Replace rest_client with exchange_service parameter
    - Update _verify_position_exists to use exchange_service
    - _Requirements: 1.4_

  - [ ] 7.2 Enhance _recover_halted method with safety checks
    - Log warning "Bot bị tắt khi đang HALTED. Giữ nguyên trạng thái dừng."
    - Return action="blocked" instead of "restored"
    - Publish status event with manual intervention message
    - _Requirements: 3.1, 3.2, 3.3_
  - [ ]* 7.3 Write property test for HALTED recovery safety
    - **Property 5: HALTED State Recovery Safety**

    - **Validates: Requirements 3.1**



- [ ] 8. Update HardFilters to use config
  - [ ] 8.1 Inject Config into HardFilters
    - Update constructor to accept Config parameter
    - Use config.book_ticker.max_age_seconds instead of hardcoded value

    - _Requirements: 2.3_


  - [x]* 8.2 Write property test for data freshness comparison

    - **Property 3: Data Freshness Comparison**
    - **Validates: Requirements 2.3**




- [ ] 9. Update DIContainer wiring
  - [ ] 9.1 Update get_state_recovery_service()
    - Use get_exchange_service() instead of get_rest_client()
    - _Requirements: 1.4_
  - [ ] 9.2 Update get_hard_filters()
    - Inject Config instance
    - _Requirements: 2.3_

- [ ] 10. Add HALTED state trading prevention
  - [ ] 10.1 Add trading operation guards
    - Check HALTED state before any trading operation
    - Reject operations with appropriate error
    - _Requirements: 3.4_
  - [ ]* 10.2 Write property test for HALTED trading prevention
    - **Property 6: HALTED State Trading Prevention**
    - **Validates: Requirements 3.4**

- [x] 11. Final Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.
