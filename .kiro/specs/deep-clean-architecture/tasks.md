# Implementation Plan

## Phase 1: Architecture Analysis & Property Tests

- [x] 1. Tạo architecture analysis tools





  - [-] 1.1 Tạo utility functions để scan imports từ Python files



    - Sử dụng AST để parse imports
    - _Requirements: 7.3_
  - [ ] 1.2 Tạo utility functions để scan React/TypeScript imports
    - _Requirements: 5.2, 5.3_
  - [ ]* 1.3 Write property test: Domain layer independence
    - **Property 1: Domain Layer Independence**
    - **Validates: Requirements 1.1**
  - [ ]* 1.4 Write property test: Import direction compliance
    - **Property 9: Import Direction Compliance**
    - **Validates: Requirements 7.3**

- [ ] 2. Checkpoint - Run architecture analysis
  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: Domain Layer Cleanup

- [ ] 3. Review và fix Domain entities
  - [ ] 3.1 Audit `src/domain/entities/` - remove any infrastructure imports
    - Check: candle.py, indicator.py, market_data.py, etc.
    - _Requirements: 1.1, 1.2_
  - [ ] 3.2 Audit `src/domain/repositories/` - ensure only abstract interfaces
    - Check: market_data_repository.py, i_order_repository.py
    - _Requirements: 1.3_
  - [ ] 3.3 Move any concrete implementations to Infrastructure
    - _Requirements: 3.1_
  - [ ]* 3.4 Write property test: Domain repository abstraction
    - **Property 2: Domain Repository Abstraction**
    - **Validates: Requirements 1.3**

- [ ] 4. Checkpoint - Domain layer clean
  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Application Layer Cleanup

- [ ] 5. Review Application services dependencies
  - [ ] 5.1 Audit `src/application/services/` imports
    - Identify any direct infrastructure imports
    - _Requirements: 2.1_
  - [ ] 5.2 Refactor RealtimeService - extract infrastructure dependencies
    - Use dependency injection for all external dependencies
    - _Requirements: 2.1, 2.3_
  - [ ] 5.3 Refactor SignalGenerator - use interfaces instead of concrete classes
    - _Requirements: 2.1, 2.3_
  - [ ]* 5.4 Write property test: Application layer dependencies
    - **Property 3: Application Layer Dependencies**
    - **Validates: Requirements 2.1**

- [ ] 6. Move calculators to correct layer
  - [ ] 6.1 Review calculators in `application/services/`
    - entry_price_calculator, tp_calculator, stop_loss_calculator, confidence_calculator
    - Determine if they belong in Application or Infrastructure
    - _Requirements: 2.2_
  - [ ] 6.2 Move pure calculation logic to Infrastructure if needed
    - _Requirements: 3.4_

- [ ] 7. Checkpoint - Application layer clean
  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: Infrastructure Layer Cleanup

- [ ] 8. Verify Infrastructure isolation
  - [ ] 8.1 Audit external API usage - ensure only in Infrastructure
    - Check for requests, httpx, websockets imports
    - _Requirements: 3.2_
  - [ ] 8.2 Audit database usage - ensure only in Infrastructure
    - Check for sqlite3 imports
    - _Requirements: 3.3_
  - [ ]* 8.3 Write property test: Infrastructure isolation - APIs
    - **Property 4: Infrastructure Isolation - External APIs**
    - **Validates: Requirements 3.2**
  - [ ]* 8.4 Write property test: Infrastructure isolation - Database
    - **Property 5: Infrastructure Isolation - Database**
    - **Validates: Requirements 3.3**

- [ ] 9. Checkpoint - Infrastructure layer clean
  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Presentation Layer (Backend API) Cleanup

- [ ] 10. Review API routers
  - [ ] 10.1 Audit `src/api/routers/` imports
    - Ensure they only import from Application layer
    - _Requirements: 4.1_
  - [ ] 10.2 Refactor routers to use Application services only
    - Remove any direct Infrastructure imports
    - _Requirements: 4.1_
  - [ ] 10.3 Review `src/api/dependencies.py` - ensure proper DI setup
    - _Requirements: 6.1, 6.2_
  - [ ]* 10.4 Write property test: Presentation layer dependencies
    - **Property 6: Presentation Layer Dependencies**
    - **Validates: Requirements 4.1**

- [ ] 11. Checkpoint - Backend API clean
  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Frontend (React) Cleanup

- [ ] 12. Review React components
  - [ ] 12.1 Audit `frontend/src/components/` for direct API calls
    - Move fetch/axios calls to hooks
    - _Requirements: 5.2, 5.3_
  - [ ] 12.2 Refactor App.tsx - extract business logic to hooks/services
    - _Requirements: 5.1, 5.4_
  - [ ] 12.3 Review hooks structure - ensure proper separation
    - _Requirements: 5.2_
  - [ ]* 12.4 Write property test: Frontend state separation
    - **Property 7: Frontend State Separation**
    - **Validates: Requirements 5.2, 5.3**

- [ ] 13. Checkpoint - Frontend clean
  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: Dependency Injection Consistency

- [ ] 14. Review DI container and usage
  - [ ] 14.1 Audit `src/infrastructure/di_container.py`
    - Ensure all services are registered
    - _Requirements: 6.2_
  - [ ] 14.2 Audit service constructors - ensure DI pattern
    - Check for internal instantiation of dependencies
    - _Requirements: 6.1_
  - [ ] 14.3 Refactor any services not using DI
    - _Requirements: 6.1_
  - [ ]* 14.4 Write property test: DI consistency
    - **Property 8: Dependency Injection Consistency**
    - **Validates: Requirements 6.1**

- [ ] 15. Final Checkpoint - All architecture tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 8: Documentation & Final Verification

- [ ] 16. Update documentation
  - [ ] 16.1 Update README with architecture overview
    - _Requirements: 7.1_
  - [ ] 16.2 Add architecture decision records (ADRs) if needed
    - _Requirements: 7.2_

- [ ] 17. Final verification
  - [ ] 17.1 Run all property tests
    - _Requirements: 1.1, 2.1, 3.2, 3.3, 4.1, 5.2, 6.1, 7.3_
  - [ ] 17.2 Run full test suite
    - _Requirements: All_
  - [ ] 17.3 Verify backend starts without errors
    - _Requirements: All_
