# Implementation Plan

## Phase 0: Backup và Chuẩn bị

- [x] 1. Tạo git branch cho cleanup



  - Tạo branch mới: `git checkout -b chore/cleanup-20251126`
  - Commit trạng thái hiện tại trước khi bắt đầu
  - _Requirements: 1.1_






## Phase 1: Xóa File Rác và Cấu hình Cũ















- [x] 2. Xóa database files không sử dụng
  - [x] 2.1 Xóa `nonexistent.db` từ project root (không tồn tại - skipped)
    - _Requirements: 2.1, 1.2_
  - [x] 2.2 Xóa `crypto_data.db` từ project root
    - Data đã migrate sang `data/trading_system.db`
    - _Requirements: 2.2, 1.2_

- [x] 3. Xóa Streamlit remnants và scripts cũ
  - [x] 3.1 Xóa folder `.streamlit/` và toàn bộ nội dung
    - _Requirements: 2.3_
  - [x] 3.2 Xóa `launch_dashboard.bat` (không tồn tại - skipped)
    - _Requirements: 2.4_

- [x] 4. Xóa cache folders
  - [x] 4.1 Tìm và xóa tất cả `__pycache__/` folders trong project
    - _Requirements: 2.5_
  - [ ]* 4.2 Write property test: No pycache folders remain
    - **Property 2: No Pycache Folders Remain**
    - **Validates: Requirements 2.5**



## Phase 2: Xóa Code Duplicate

- [x] 5. Xóa duplicate files trong src/
  - [x] 5.1 Xóa `src/binance_client.py`
    - Đã được thay thế bởi `src/infrastructure/api/binance_rest_client.py`
    - _Requirements: 3.1_
  - [x] 5.2 Xóa `src/indicators.py`
    - Đã được thay thế bởi modules trong `src/infrastructure/indicators/`
    - _Requirements: 3.2_
  - [x] 5.3 Xóa `src/database.py`
    - Đã được thay thế bởi `src/infrastructure/persistence/sqlite_order_repository.py`
    - _Requirements: 3.3_
  - [x] 5.4 Xóa `src/pipeline.py`
    - Đã được thay thế bởi service layer
    - _Requirements: 3.4_

- [x] 6. Xóa debug scripts
  - [x] 6.1 Xóa folder `scripts/debug/` nếu tồn tại (không tồn tại - skipped)
    - _Requirements: 4.1_
  - [x] 6.2 Xóa tất cả files `scripts/backtesting/debug_*.py`
    - _Requirements: 4.2_
  - [ ]* 6.3 Write property test: No debug files remain
    - **Property 3: No Debug Files Remain**
    - **Validates: Requirements 4.2**

## Phase 3: Cập nhật Import Paths

- [x] 7. Cập nhật imports cho các file đã xóa
  - [x] 7.1 Tìm và cập nhật tất cả imports từ `src.database` (không có imports cũ)
    - _Requirements: 5.1_
  - [x] 7.2 Tìm và cập nhật tất cả imports từ `src.binance_client` (không có imports cũ)
    - _Requirements: 5.2_
  - [x] 7.3 Tìm và cập nhật tất cả imports từ `src.indicators` (không có imports cũ)
    - _Requirements: 5.3_
  - [x] 7.4 Verify syntax của tất cả files đã update
    - Chạy `python -m py_compile` trên mỗi file - PASSED
    - _Requirements: 5.4_
  - [ ]* 7.5 Write property test: Import path consistency
    - **Property 4: Import Path Consistency**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  - [ ]* 7.6 Write property test: Functional preservation
    - **Property 5: Functional Preservation After Import Update**
    - **Validates: Requirements 5.4**

- [x] 8. Checkpoint - Verify imports
  - All Python files compiled successfully
  - Core imports verified working
  - Checkpoint commit created

## Phase 4: Hợp nhất Repository

- [-] 9. Consolidate repository implementations
  - [x] 9.1 Review repositories - Quyết định di chuyển thay vì merge (2 repos có mục đích khác nhau)
    - Di chuyển `sqlite_repository.py` → `persistence/sqlite_market_data_repository.py`
    - Xóa folder `database/` (trống)
    - _Requirements: 6.1_
  - [x] 9.2 Cập nhật imports trong `di_container.py` và `__init__.py`
    - _Requirements: 6.2_
  - [x] 9.3 Verify imports hoạt động đúng
    - _Requirements: 6.3_
  - [ ]* 9.4 Write property test: Repository import consistency
    - **Property 6: Repository Import Consistency**
    - **Validates: Requirements 6.3**

## Phase 5: Tổ chức lại Test Files

- [ ] 10. Di chuyển test files vào đúng thư mục
  - [ ] 10.1 Di chuyển `test_backend.py` → `tests/integration/test_backend_flow.py`
    - Tạo folder `tests/integration/` nếu chưa tồn tại
    - _Requirements: 7.1_
  - [ ] 10.2 Di chuyển `test_integration.py` → `tests/integration/test_full_system.py`
    - _Requirements: 7.2_
  - [ ] 10.3 Cập nhật relative imports trong các test files đã di chuyển
    - _Requirements: 7.3_
  - [ ]* 10.4 Write property test: Moved test files work correctly
    - **Property 7: Moved Test Files Work Correctly**
    - **Validates: Requirements 7.3**

## Phase 6: Final Verification

- [ ] 11. Chạy verification tests
  - [ ] 11.1 Chạy `pytest tests/` và verify tất cả tests pass
    - _Requirements: 8.1, 8.3_



  - [ ] 11.2 Khởi động backend với `uvicorn src.api.main:app`
    - Verify không có ModuleNotFoundError
    - _Requirements: 8.2, 8.4_

- [ ] 12. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
