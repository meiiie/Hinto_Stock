# LUỒNG NGOÀI - Human Workspace

Folder này dành cho **con người** - bạn, đồng nghiệp, và các chuyên gia tư vấn.

---

## BẮT ĐẦU TỪ ĐÂY

### Bước 1: Mở bất kỳ AI nào
(Claude, GPT, Gemini, hoặc AI trong IDE)

### Bước 2: Gửi prompt này

```
Chào bạn, bạn là Workspace Navigator AI.
Đọc file e:\Sach\DuAn\Hinto_Stock\documents\luongngoai\navigator\system-prompt.md
```

### Bước 3: Navigator sẽ hỏi bạn

```
Navigator Ready.
Workspace hiện tại: Hinto Stock Trading

Bạn muốn:
1. Tiếp tục làm việc với dự án hiện tại
2. Khởi tạo workspace cho DỰ ÁN MỚI

Chọn (1 hoặc 2):
```

### Bước 4: Làm theo hướng dẫn

- **Chọn 1**: Navigator sẽ trả lời câu hỏi, routing đến agent phù hợp
- **Chọn 2**: Navigator sẽ dẫn đến prompt khởi tạo dự án mới

---

## Flowchart tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 1: Mở bất kỳ AI nào (Claude, GPT, Gemini...)          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 2: Gửi prompt Navigator (copy ở trên)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 3: Navigator hỏi: Chọn 1 hay 2?                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌─────────────────────┐    ┌─────────────────────────────────┐
│  CHỌN 1:            │    │  CHỌN 2:                        │
│  Làm việc project   │    │  Khởi tạo cho dự án mới         │
│  hiện tại           │    │                                 │
└──────────┬──────────┘    └────────────────┬────────────────┘
           │                                │
           ▼                                ▼
┌─────────────────────┐    ┌─────────────────────────────────┐
│  Hỏi câu hỏi        │    │  Navigator dẫn đến              │
│  (tổng quan, bug,   │    │  prompt-khoi-tao-du-an-moi.md   │
│  architecture...)   │    │                                 │
└──────────┬──────────┘    └─────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 4: Navigator gợi ý agent phù hợp                      │
│  (BE AI, FE AI, QA AI...)                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 5: Mở CHAT MỚI hoặc IDE khác                          │
│  Dùng prompt agent được gợi ý                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Ví dụ thực tế

**Bạn**: "Tôi muốn fix bug backend"

**Navigator**:
```
Dùng Backend Engineer AI.

Prompt (mở chat/IDE mới, copy này):
"Chào bạn, bạn là Backend Engineer AI.
Đọc file .../ai-workspace/agents/backend-engineer/system-prompt.md"

Rồi hỏi về bug cần fix.
```

**Bạn**: "Tôi muốn phân tích strategy trading"

**Navigator**:
```
Dùng Quant Specialist AI.

Prompt:
"Chào bạn, bạn là Quant Specialist AI.
Đọc file .../ai-workspace/agents/quant-specialist/system-prompt.md"
```

**Bạn**: Mở VS Code/Cursor/ChatGPT mới → Paste prompt → Làm việc!

---

## Cấu trúc folder

```
luongngoai/
├── README.md                 # File này
├── navigator/                # ĐIỂM BẮT ĐẦU
│   └── system-prompt.md      
├── quytrinhAI/               
│   ├── huong-dan-su-dung.md  
│   └── prompt-khoi-tao-du-an-moi.md  
├── chuyen-gia/               
├── quytac/                   
└── prompt/                   
```

---

Updated: 2025-12-23
