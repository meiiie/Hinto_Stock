# Requirements Document

## Introduction

Dự án Hinto_Stock đã tích lũy technical debt đáng kể trong quá trình phát triển, bao gồm file rác, code trùng lặp, và tàn dư từ Streamlit cũ. Spec này định nghĩa các yêu cầu để dọn dẹp và tái cấu trúc dự án một cách an toàn, đảm bảo hệ thống vẫn hoạt động bình thường sau khi cleanup.

## Glossary

- **Technical Debt**: Code hoặc file không còn cần thiết nhưng vẫn tồn tại trong dự án
- **Cleanup_System**: Hệ thống thực hiện việc dọn dẹp và tái cấu trúc dự án
- **Duplicate_File**: File có chức năng tương tự đã được implement ở vị trí khác theo Clean Architecture
- **Orphan_File**: File không được sử dụng bởi bất kỳ module nào trong hệ thống
- **Import_Path**: Đường dẫn import module trong Python
- **Test_Suite**: Bộ test bao gồm unit tests và integration tests

## Requirements

### Requirement 1: Backup và An toàn

**User Story:** As a developer, I want to create a backup before cleanup, so that I can restore the project if something goes wrong.

#### Acceptance Criteria

1. WHEN the cleanup process starts THEN the Cleanup_System SHALL create a new git branch named `chore/cleanup-{date}` for tracking changes
2. WHEN a file is marked for deletion THEN the Cleanup_System SHALL verify the file exists before attempting deletion
3. IF a deletion operation fails THEN the Cleanup_System SHALL log the error and continue with remaining operations

### Requirement 2: Xóa File Rác và Cấu hình Cũ

**User Story:** As a developer, I want to remove obsolete files and configurations, so that the project structure is clean and maintainable.

#### Acceptance Criteria

1. WHEN cleaning obsolete database files THEN the Cleanup_System SHALL remove `nonexistent.db` from project root
2. WHEN cleaning obsolete database files THEN the Cleanup_System SHALL remove `crypto_data.db` from project root (data đã migrate sang `trading_system.db`)
3. WHEN cleaning Streamlit remnants THEN the Cleanup_System SHALL remove the `.streamlit/` folder and all its contents
4. WHEN cleaning obsolete scripts THEN the Cleanup_System SHALL remove `launch_dashboard.bat` from project root
5. WHEN cleaning cache files THEN the Cleanup_System SHALL remove all `__pycache__/` folders throughout the project

### Requirement 3: Xóa Code Duplicate

**User Story:** As a developer, I want to remove duplicate code files, so that imports are unambiguous and maintenance is simplified.

#### Acceptance Criteria

1. WHEN removing duplicate binance client THEN the Cleanup_System SHALL delete `src/binance_client.py` (replaced by `src/infrastructure/api/binance_rest_client.py`)
2. WHEN removing duplicate indicators THEN the Cleanup_System SHALL delete `src/indicators.py` (replaced by modules in `src/infrastructure/indicators/`)
3. WHEN removing duplicate database THEN the Cleanup_System SHALL delete `src/database.py` (replaced by `src/infrastructure/persistence/sqlite_order_repository.py`)
4. WHEN removing obsolete pipeline THEN the Cleanup_System SHALL delete `src/pipeline.py` (replaced by service layer)

### Requirement 4: Xóa Script Debug/Test Tạm

**User Story:** As a developer, I want to remove temporary debug scripts, so that the scripts folder only contains production-ready code.

#### Acceptance Criteria

1. WHEN cleaning debug scripts THEN the Cleanup_System SHALL remove the entire `scripts/debug/` folder if it exists
2. WHEN cleaning debug scripts THEN the Cleanup_System SHALL remove all files matching pattern `scripts/backtesting/debug_*.py`

### Requirement 5: Cập nhật Import Paths

**User Story:** As a developer, I want all import paths updated after file deletion, so that the application runs without ModuleNotFoundError.

#### Acceptance Criteria

1. WHEN a duplicate file is deleted THEN the Cleanup_System SHALL update all files importing from `src.database` to use `src.infrastructure.persistence.sqlite_order_repository`
2. WHEN a duplicate file is deleted THEN the Cleanup_System SHALL update all files importing from `src.binance_client` to use `src.infrastructure.api.binance_rest_client`
3. WHEN a duplicate file is deleted THEN the Cleanup_System SHALL update all files importing from `src.indicators` to use appropriate modules in `src.infrastructure.indicators`
4. WHEN imports are updated THEN the Cleanup_System SHALL preserve the original functionality of each importing module

### Requirement 6: Hợp nhất Repository Files

**User Story:** As a developer, I want repository implementations consolidated, so that there is a single source of truth for data access.

#### Acceptance Criteria

1. WHEN consolidating repositories THEN the Cleanup_System SHALL merge necessary logic from `src/infrastructure/database/sqlite_repository.py` into `src/infrastructure/persistence/sqlite_order_repository.py`
2. WHEN consolidation is complete THEN the Cleanup_System SHALL delete `src/infrastructure/database/sqlite_repository.py`
3. WHEN repository is consolidated THEN the Cleanup_System SHALL update all imports referencing the deleted file

### Requirement 7: Tổ chức lại Test Files

**User Story:** As a developer, I want test files organized in proper directories, so that the test structure follows best practices.

#### Acceptance Criteria

1. WHEN organizing test files THEN the Cleanup_System SHALL move `test_backend.py` from root to `tests/integration/test_backend_flow.py`
2. WHEN organizing test files THEN the Cleanup_System SHALL move `test_integration.py` from root to `tests/integration/test_full_system.py`
3. WHEN test files are moved THEN the Cleanup_System SHALL update any relative imports within the moved files

### Requirement 8: Verification sau Cleanup

**User Story:** As a developer, I want to verify the system works after cleanup, so that I can be confident no functionality was broken.

#### Acceptance Criteria

1. WHEN cleanup is complete THEN the Cleanup_System SHALL run `pytest tests/` and report results
2. WHEN cleanup is complete THEN the Cleanup_System SHALL verify the backend starts successfully with `uvicorn src.api.main:app`
3. IF any test fails after cleanup THEN the Cleanup_System SHALL report the failing test details
4. IF backend fails to start THEN the Cleanup_System SHALL report the ModuleNotFoundError or other startup errors
