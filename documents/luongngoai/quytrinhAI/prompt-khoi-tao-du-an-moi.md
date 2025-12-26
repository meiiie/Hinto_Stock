# PROMPT TEMPLATE: Khởi tạo AI Workspace cho Dự Án Mới

File này chứa các prompt template để khởi tạo AI Workspace cho một dự án mới.
Copy và điều chỉnh các prompt này khi bắt đầu với project khác.

---

## BƯỚC 1: AUDIT TOÀN BỘ DỰ ÁN

### Prompt để AI audit và hiểu dự án

```
Tôi có một AI Workspace template tại [PATH_TO_AI_WORKSPACE].
Dự án hiện tại là [TÊN DỰ ÁN] - [MÔ TẢ NGẮN].

Tôi cần bạn:

1. NGHIÊN CỨU SÂU toàn bộ codebase:
   - Rà soát từng folder để hiểu cấu trúc thực tế
   - Xác định tech stack (frontend, backend, database)
   - Map các components, services, entities chính
   - Ghi nhận các patterns đang sử dụng

2. CẬP NHẬT AI WORKSPACE:
   - Cập nhật progress.md của mỗi agent với thông tin thực tế từ codebase
   - Cập nhật shared-board.md với trạng thái hiện tại
   - Đảm bảo context files phản ánh đúng dự án

Lưu ý:
- Suy nghĩ thật kỹ và cẩn thận
- Rà soát từng folder để có cái nhìn chính xác
- Đừng sửa chắp vá, hãy làm đúng chuẩn
- Agent AI cần hiểu biết chất lượng về codebase

Bắt đầu với việc list tất cả folders trong project.
```

---

## BƯỚC 2: AUDIT TỪNG LAYER

### 2.1 Prompt Audit Backend

```
Bạn là Backend Engineer AI.
Đọc file [PATH]/ai-workspace/README.md để hiểu context.

Nhiệm vụ: AUDIT BACKEND CODEBASE

1. Rà soát toàn bộ backend:
   - Cấu trúc folders (src/, app/, server/...)
   - Framework sử dụng (FastAPI, Django, Express...)
   - API endpoints có sẵn
   - Services và business logic
   - Patterns (Clean Architecture? MVC? Hexagonal?)

2. Tạo file progress.md chính xác:
   - Map tất cả files quan trọng
   - Ghi nhận status từng component
   - List các dependencies
   - Known issues nếu có

Suy nghĩ thật sâu. Rà soát từng folder một cách thực tế.
Bắt đầu với: list e:\Path\To\Project\src
```

### 2.2 Prompt Audit Frontend

```
Bạn là Frontend Architect AI.
Đọc file [PATH]/ai-workspace/README.md để hiểu context.

Nhiệm vụ: AUDIT FRONTEND CODEBASE

1. Rà soát toàn bộ frontend:
   - Framework (React, Angular, Vue...)
   - State management (Redux, Zustand, Pinia...)
   - Styling (TailwindCSS, SCSS, CSS Modules...)
   - Components structure
   - Routing setup

2. Tạo file progress.md chính xác:
   - List tất cả components và chức năng
   - Map hooks và utilities
   - Design system hiện tại
   - Dependencies và versions

Suy nghĩ thật sâu. Rà soát từng folder một cách thực tế.
```

### 2.3 Prompt Audit Database

```
Bạn là Database Specialist AI.
Đọc file [PATH]/ai-workspace/README.md để hiểu context.

Nhiệm vụ: AUDIT DATABASE LAYER

1. Rà soát persistence layer:
   - Database type (PostgreSQL, MySQL, SQLite, MongoDB...)
   - ORM (SQLAlchemy, Prisma, TypeORM...)
   - Schema/migrations
   - Repositories pattern

2. Tạo file progress.md chính xác:
   - Schema hiện tại (tables, relations)
   - Repository methods
   - Migration status
   - Known issues

Suy nghĩ thật sâu. Tìm hiểu kỹ schema và data flow.
```

### 2.4 Prompt Audit QA/Testing

```
Bạn là QA Engineer AI.
Đọc file [PATH]/ai-workspace/README.md để hiểu context.

Nhiệm vụ: AUDIT TESTING SETUP

1. Rà soát test infrastructure:
   - Test framework (Jest, Pytest, Vitest...)
   - Test types (unit, integration, e2e)
   - Coverage tools
   - CI/CD integration

2. Tạo file progress.md chính xác:
   - List test files và coverage
   - Testing gaps
   - Known bugs/issues
   - Test patterns đang dùng

Suy nghĩ thật sâu. Đánh giá test quality thực tế.
```

---

## BƯỚC 3: CẬP NHẬT SYSTEM PROMPTS (NẾU CẦN)

### Prompt để restructure theo SOTA

```
Tôi muốn cập nhật SYSTEM PROMPT của các AI agents theo chuẩn SOTA.

Yêu cầu:
1. Nghiên cứu các kỹ thuật prompt engineering hiện đại nhất
   - Từ các tổ chức: LangChain, CrewAI, Anthropic, OpenAI
   - Các patterns: ReAct, CoT, PTCF, Meta-Prompting
   - Tính tới thời điểm [NGÀY HIỆN TẠI]

2. Áp dụng best practices:
   - XML tags structuring (Anthropic style)
   - ReAct pattern cho reasoning
   - Chain-of-Thought triggers
   - No emojis (professional standard)

3. Tái cấu trúc system-prompt.md cho [AGENT]:
   - Giữ nguyên domain knowledge
   - Cập nhật format theo SOTA
   - Thêm guardrails phù hợp

Lưu ý:
- KHÔNG sửa chắp vá
- Theo đúng best practices từ các tổ chức lớn
- Suy nghĩ thật kỹ trước khi implement
```

---

## BƯỚC 4: VERIFY VÀ FINALIZE

### Prompt kiểm tra hoàn thiện

```
Kiểm tra AI Workspace đã hoàn thiện chưa:

1. Mỗi agent có:
   - [ ] system-prompt.md cập nhật
   - [ ] context/progress.md phản ánh đúng codebase
   - [ ] Templates nếu cần

2. Shared context có:
   - [ ] shared-board.md với status thực tế
   - [ ] decision-log.md
   - [ ] global-architecture.md mô tả đúng dự án

3. Communication có:
   - [ ] agent-handoffs.md
   - [ ] conflict-resolution.md

4. Workflows phù hợp với dự án

Báo cáo những gì còn thiếu hoặc cần cập nhật.
```

---

## QUICK TEMPLATE

### One-shot audit prompt (Copy và dùng ngay)

```
Tôi có AI Workspace tại: [PATH_TO_AI_WORKSPACE]
Dự án: [TÊN DỰ ÁN]
Tech stack dự kiến: [FE: React/Vue...] [BE: FastAPI/Django...] [DB: PostgreSQL/...]

Nhiệm vụ:
1. Audit toàn bộ codebase thực tế
2. Cập nhật tất cả progress.md files cho từng agent (BE, FE, DB, QA)
3. Cập nhật shared-board.md với trạng thái thực tế
4. Báo cáo những gì phát hiện được

Yêu cầu:
- Rà soát từng folder một cách kỹ lưỡng
- Ghi nhận thực tế, không giả định
- Cập nhật files với thông tin chính xác

Bắt đầu với: list [PROJECT_ROOT]
```

---

## LƯU Ý QUAN TRỌNG

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  Luôn để AI rà soát THỰC TẾ, không giả định              │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  Mỗi dự án khác nhau, progress.md phải reflect đúng     │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  Dùng ULTRATHINK cho phân tích phức tạp                 │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  Backup trước khi AI cập nhật files                      │
└─────────────────────────────────────────────────────────────┘
```

---

Updated: 2025-12-23
