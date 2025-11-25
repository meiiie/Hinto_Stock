🏗️ SOFTWARE ARCHITECTURE DOCUMENT: HINTO TRADER PRO (DESKTOP)
Date: 23/11/2025
Architect: Chief Architect
Version: 1.0
Target: Frontend & Backend Team
1. TỔNG QUAN (OVERVIEW)
Chúng ta sẽ chuyển đổi giao diện từ Web Dashboard (Streamlit) sang Native Desktop Application.
Mục tiêu: Hiệu năng cao (60fps), giao diện chuyên nghiệp như Binance Desktop, bảo mật dữ liệu Local-first.
Mô hình: Client-Server (Local). Ứng dụng Desktop sẽ không kết nối trực tiếp tới Binance mà kết nối tới Trading Engine (Python) để đảm bảo tính nhất quán dữ liệu (Single Source of Truth).
2. CÔNG NGHỆ (TECH STACK)
A. Core System (Giữ nguyên Layer 1)
Language: Python 3.x
Database: SQLite (chế độ WAL mode).
Trading Engine: RealtimeService (Singleton).
B. Middleware (Lớp trung gian - Cần xây dựng mới)
API Framework: FastAPI (Python).
Role: Đọc dữ liệu từ SQLite và TradingEngine để trả về JSON cho Frontend.
Communication: HTTP REST (cho dữ liệu tĩnh) + WebSocket (cho giá real-time).
C. Presentation (Desktop Client - Cần xây dựng mới)
Wrapper: Tauri v2 (Rust). Dùng để đóng gói web thành file .exe/.dmg. Siêu nhẹ, bảo mật.
Frontend Framework: React (TypeScript) + Vite.
UI Library: TailwindCSS (Styling) + ShadcnUI (Components).
State Management: Zustand (hoặc React Query).
Charting: TradingView Lightweight Charts (Chuẩn mực tài chính).
3. SƠ ĐỒ KIẾN TRÚC (ARCHITECTURE DIAGRAM)
code
Mermaid
graph TD
    subgraph "Desktop Application (Tauri Window)"
        UI[React Frontend]
        Chart[TradingView Chart]
        Store[Zustand State]
    end

    subgraph "Local Python Process (Backend)"
        API[FastAPI Server]
        Bot[Trading Engine]
    end

    subgraph "Data Layer"
        DB[(SQLite DB)]
    end

    Exchange((Binance API))

    %% Luồng dữ liệu
    Exchange -->|WebSocket Price| Bot
    Bot -->|Write Orders| DB
    Bot -.->|Shared Memory| API
    API -->|Read History| DB
    
    %% Giao tiếp Frontend - Backend
    UI -->|HTTP GET /status| API
    UI -->|HTTP GET /history| API
    API -->|WebSocket /stream| UI
4. QUY HOẠCH API (API SPECIFICATION)
Team Backend cần triển khai FastAPI với các endpoints sau để Frontend gọi:
Base URL: http://localhost:8000/api/v1
Method	Endpoint	Mô tả
GET	/status	Trả về trạng thái Bot (Running/Stopped), PnL hiện tại, Giá BTC hiện tại.
GET	/account	Trả về Số dư (Balance), Equity, Margin Used.
GET	/positions	Trả về danh sách lệnh đang mở (Active Positions).
GET	/history	Trả về lịch sử giao dịch (có phân trang).
GET	/candles	Trả về dữ liệu nến (OHLCV) để vẽ biểu đồ.
POST	/settings	Cập nhật tham số (Risk, R:R, Trailing Config).
5. CẤU TRÚC DỰ ÁN MỚI (FOLDER STRUCTURE)
Chúng ta sẽ tổ chức theo dạng Monorepo (Một kho chứa cả Frontend và Backend mới):
code
Text
Hinto_Stock/
├── src/                     # Code Python cũ (Trading Engine)
│   ├── application/
│   └── ...
├── src-tauri/               # Cấu hình Rust cho Desktop App
├── src-ui/                  # 🆕 Code React Frontend
│   ├── src/
│   │   ├── components/      # UI: Button, Table, Modal
│   │   ├── charts/          # Code vẽ biểu đồ TradingView
│   │   ├── hooks/           # Logic gọi API (React Query)
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── api/                     # 🆕 Code FastAPI
│   ├── main.py              # Server entry point
│   └── routers/
└── ...
6. LỘ TRÌNH THỰC HIỆN (ROADMAP)
Giai đoạn 1: Chuẩn bị Backend (2 ngày)
Backend Dev: Viết api/main.py sử dụng FastAPI.
Kết nối FastAPI vào trading_system.db.
Tạo endpoint /status và /positions để test dữ liệu.
Giai đoạn 2: Dựng khung Frontend (3 ngày)
Frontend Dev: Khởi tạo dự án Tauri + React + Vite.
Cài đặt TailwindCSS và ShadcnUI.
Dựng Layout chính: Sidebar, Header, Content Area (như Binance).
Giai đoạn 3: Tích hợp Biểu đồ (Quan trọng nhất - 2 ngày)
Cài đặt lightweight-charts.
Viết Component nhận dữ liệu nến từ API và vẽ lên màn hình.
Vẽ thêm các "Marker" (Mũi tên Xanh/Đỏ) tại các điểm Bot vào lệnh.
7. LƯU Ý KỸ THUẬT (TECHNICAL NOTES)
CORS: Khi phát triển, Frontend chạy port 3000, Backend chạy port 8000. Nhớ cấu hình CORS trong FastAPI để cho phép kết nối.
Sidecar Pattern: Khi đóng gói (Build) ra file .exe cuối cùng, chúng ta sẽ dùng tính năng Sidecar của Tauri để nhúng file Python (main.exe) vào trong App. Khi người dùng bật App, Python Server sẽ tự chạy ngầm bên dưới.
Real-time: Tạm thời ở version 1, Frontend có thể dùng cơ chế Polling (gọi API mỗi 1 giây) để cập nhật giá. Version 2 sẽ nâng cấp lên WebSocket.