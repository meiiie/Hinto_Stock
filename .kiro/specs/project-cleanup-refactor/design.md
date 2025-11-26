# Design Document: Project Cleanup and Refactor

## Overview

Thiết kế này mô tả quy trình dọn dẹp và tái cấu trúc dự án Hinto_Stock một cách an toàn và có hệ thống. Quy trình được chia thành các phase riêng biệt, mỗi phase có verification step để đảm bảo không làm hỏng hệ thống.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLEANUP WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│  Phase 0: Backup                                             │
│  ├── Create git branch: chore/cleanup-{date}                │
│  └── Commit current state                                    │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: Delete Obsolete Files                              │
│  ├── Database files (nonexistent.db, crypto_data.db)        │
│  ├── Streamlit remnants (.streamlit/)                       │
│  ├── Old scripts (launch_dashboard.bat)                     │
│  └── Cache folders (__pycache__/)                           │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: Delete Duplicate Code                              │
│  ├── src/binance_client.py                                  │
│  ├── src/indicators.py                                      │
│  ├── src/database.py                                        │
│  └── src/pipeline.py                                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: Update Import Paths                                │
│  ├── Find all files importing deleted modules               │
│  ├── Update import statements                               │
│  └── Verify syntax correctness                              │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: Consolidate Repositories                           │
│  ├── Merge sqlite_repository.py logic                       │
│  ├── Delete sqlite_repository.py                            │
│  └── Update imports                                         │
├─────────────────────────────────────────────────────────────┤
│  Phase 5: Organize Test Files                                │
│  ├── Move test_backend.py → tests/integration/              │
│  ├── Move test_integration.py → tests/integration/          │
│  └── Update relative imports                                │
├─────────────────────────────────────────────────────────────┤
│  Phase 6: Verification                                       │
│  ├── Run pytest tests/                                      │
│  ├── Start uvicorn server                                   │
│  └── Report results                                         │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### File Deletion Component

Xử lý việc xóa file an toàn với logging.

```python
# Pseudocode for safe file deletion
def safe_delete(file_path: str) -> bool:
    if not exists(file_path):
        log(f"File not found: {file_path}")
        return False
    try:
        delete(file_path)
        log(f"Deleted: {file_path}")
        return True
    except Exception as e:
        log(f"Error deleting {file_path}: {e}")
        return False
```

### Import Update Component

Tìm và cập nhật import statements.

```python
# Import mapping
IMPORT_MAPPING = {
    "from src.database import": "from src.infrastructure.persistence.sqlite_order_repository import",
    "from src.binance_client import": "from src.infrastructure.api.binance_rest_client import",
    "from src.indicators import": "from src.infrastructure.indicators",
    "import src.database": "import src.infrastructure.persistence.sqlite_order_repository",
    "import src.binance_client": "import src.infrastructure.api.binance_rest_client",
}
```

### Test Organization Component

Di chuyển và cập nhật test files.

```
Before:
  /test_backend.py
  /test_integration.py

After:
  /tests/integration/test_backend_flow.py
  /tests/integration/test_full_system.py
```

## Data Models

### Files to Delete

| Category | File/Folder | Reason |
|----------|-------------|--------|
| Database | nonexistent.db | Orphan file, không được sử dụng |
| Database | crypto_data.db | Data đã migrate sang trading_system.db |
| Config | .streamlit/ | Streamlit không còn được sử dụng |
| Script | launch_dashboard.bat | Script cho Streamlit cũ |
| Cache | __pycache__/ | Cache files, tự động regenerate |
| Duplicate | src/binance_client.py | Replaced by infrastructure/api/binance_rest_client.py |
| Duplicate | src/indicators.py | Replaced by infrastructure/indicators/ modules |
| Duplicate | src/database.py | Replaced by infrastructure/persistence/ |
| Duplicate | src/pipeline.py | Replaced by service layer |
| Debug | scripts/debug/ | Temporary debug scripts |
| Debug | scripts/backtesting/debug_*.py | Debug scripts |

### Import Mapping Table

| Old Import | New Import |
|------------|------------|
| `from src.database import DatabaseManager` | `from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository` |
| `from src.binance_client import BinanceClient` | `from src.infrastructure.api.binance_rest_client import BinanceRestClient` |
| `from src.indicators import calculate_*` | `from src.infrastructure.indicators.{specific_module} import *` |



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: File Existence Check Before Deletion
*For any* file path marked for deletion, the cleanup system should verify the file exists before attempting deletion, preventing errors on non-existent files.
**Validates: Requirements 1.2**

### Property 2: No Pycache Folders Remain
*For any* directory in the project after cleanup, no `__pycache__/` folder should exist at any depth level.
**Validates: Requirements 2.5**

### Property 3: No Debug Files Remain
*For any* file in `scripts/backtesting/` after cleanup, no file should match the pattern `debug_*.py`.
**Validates: Requirements 4.2**

### Property 4: Import Path Consistency
*For any* Python file in the project after cleanup, no import statement should reference deleted modules (`src.database`, `src.binance_client`, `src.indicators`, `src.pipeline`).
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 5: Functional Preservation After Import Update
*For any* module that had its imports updated, the module should remain syntactically valid Python and maintain its original public interface.
**Validates: Requirements 5.4**

### Property 6: Repository Import Consistency
*For any* Python file after repository consolidation, no import should reference `src.infrastructure.database.sqlite_repository`.
**Validates: Requirements 6.3**

### Property 7: Moved Test Files Work Correctly
*For any* test file moved to `tests/integration/`, all relative imports within the file should resolve correctly from the new location.
**Validates: Requirements 7.3**

## Error Handling

### Deletion Errors
- If a file doesn't exist, log warning and continue
- If permission denied, log error with file path and continue
- If folder not empty (for rmdir), use recursive delete

### Import Update Errors
- If file cannot be parsed as Python, log error and skip
- If import pattern not found, log info (file may already be updated)
- If write fails, log error and abort that file's update

### Verification Errors
- If pytest fails, capture and report failing tests
- If uvicorn fails to start, capture ModuleNotFoundError details
- Provide rollback instructions if verification fails

## Testing Strategy

### Verification Approach

Do đây là một cleanup/refactoring task, testing strategy tập trung vào verification sau mỗi phase:

1. **After Phase 1-2 (File Deletion)**:
   - Verify deleted files no longer exist
   - Verify remaining files are intact

2. **After Phase 3 (Import Updates)**:
   - Run `python -m py_compile` on all modified files
   - Verify no syntax errors

3. **After Phase 4 (Repository Consolidation)**:
   - Verify merged repository has all required methods
   - Run related unit tests

4. **After Phase 5 (Test Organization)**:
   - Run `pytest tests/integration/` to verify moved tests work

5. **Final Verification (Phase 6)**:
   - Run full test suite: `pytest tests/`
   - Start backend: `uvicorn src.api.main:app`
   - Verify no ModuleNotFoundError

### Property-Based Testing

Sử dụng `pytest` với `hypothesis` library cho property-based tests:

```python
# Example property test for import consistency
from hypothesis import given, strategies as st
import ast
import os

@given(st.sampled_from(get_all_python_files()))
def test_no_old_imports_remain(python_file):
    """
    **Feature: project-cleanup-refactor, Property 4: Import Path Consistency**
    """
    with open(python_file) as f:
        content = f.read()
    
    old_imports = ['src.database', 'src.binance_client', 'src.indicators', 'src.pipeline']
    for old_import in old_imports:
        assert old_import not in content, f"Old import {old_import} found in {python_file}"
```

### Test Annotations

Mỗi property-based test phải được annotate với format:
- `**Feature: project-cleanup-refactor, Property {number}: {property_text}**`
