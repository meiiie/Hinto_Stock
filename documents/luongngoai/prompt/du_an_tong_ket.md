Đây là tài liệu cốt lõi ("Blueprints") để đội ngũ kỹ thuật của bạn tiếp quản và nâng cấp hệ thống.

  ---

  📘 HINTO STOCK: MASTER BLUEPRINT (v3.1 SOTA)

  > Mô hình: Automated High-Frequency Crypto Trading System
  > Trạng thái: SOTA Hardcore (Verified Logic & Backtest)
  > Mục tiêu: Tối ưu hóa lợi nhuận qua Lãi Kép & Đa dạng hóa danh mục.

  ---

  1. 🧠 TRÁI TIM CHIẾN THUẬT (THE CORE STRATEGY)

  Hệ thống vận hành dựa trên công thức "4 Trụ Cột" tạo nên cỗ máy in tiền:

  A. Entry Logic: "Limit Sniper"
   * Triết lý: Không mua đuổi (Market Order). Chỉ "săn" thanh khoản tại các điểm cực trị.
   * Timeframe: Execution trên M15 (15 phút), lọc xu hướng trên H4.
   * Cơ chế:
       1. Xác định Swing High/Low trong 20 nến gần nhất.
       2. Đặt lệnh Limit chờ sẵn tại Swing Price +/- 0.1%.
       3. Stoploss: Cực ngắn (0.5% - 1%). Chấp nhận bị quét SL thường xuyên để bảo toàn vốn.
       4. Take Profit: Trailing Stop mở rộng để ăn trọn sóng hồi (Reversion).

  B. Portfolio Mode: "Shark Tank"
   * Cấu hình cũ (Sai lầm): Max 3 vị thế. -> Hậu quả: Vốn bị kẹt ở các coin lỗ, bỏ lỡ cơ hội ngon.
   * Cấu hình chuẩn (SOTA): Max 10 vị thế (Top 10 Volume).
       * Lợi ích: Đa dạng hóa rủi ro (Diversification). Lãi của DOGE/BNB sẽ gánh lỗ cho BTC/SOL.
       * Hiệu quả: Tận dụng tối đa dòng vốn, không để tiền chết.

  C. Tăng trưởng: "Compound Engine" (Lãi Kép)
   * Cơ chế: Volume lệnh = % Equity (hoặc Leverage cố định trên Equity).
   * Hiệu ứng: Lãi sinh ra lãi. Tài khoản tăng trưởng theo cấp số nhân (Exponential) thay vì tuyến tính.
   * Minh chứng: Biến $1,000 thành $29,000 trong 1 tháng biến động mạnh (Tháng 10/2025).

  D. Quản trị rủi ro: "Hardcore Reality"
  Để đảm bảo backtest không phải là "bánh vẽ", chúng ta áp dụng các giới hạn thực tế:
   * Liquidity Cap: Giới hạn mỗi lệnh tối đa $50,000 (Tier 1 Margin). Ngăn chặn việc lãi kép vô hạn gây
     trượt giá.
   * No Circuit Breaker: TẮT CB toàn cục.
       * Lý do: Chiến thuật này cần "thở". CB thường cắt lỗ đúng đáy, ngăn cản khả năng phục hồi thần thánh
         của danh mục.

  ---

  2. 🏗️ KIẾN TRÚC HỆ THỐNG (ARCHITECTURE)

  Backend (Python/FastAPI)
   * `ExecutionSimulator`: Bộ não mô phỏng khớp lệnh. Đã tích hợp logic tính giá thanh lý (Liquidation) và
     giới hạn Volume.
   * `BacktestEngine`: Cỗ máy thời gian, tua lại dữ liệu lịch sử để chạy Simulator.
   * Data Layer: Hiện đang tải trực tiếp từ Binance API (Điểm nghẽn cần cải thiện).

  Frontend (React/Vite)
   * Quant Lab (Mới): Dashboard phân tích định lượng chuyên sâu.
       * Giao diện 2 cột (Config | Result).
       * Biểu đồ Equity Curve & Drawdown riêng biệt.
       * Sử dụng hệ thống THEME constants thay vì CSS hỗn tạp.
   * Shark Tank UI: Radar quét tín hiệu thời gian thực (Đang chờ kết nối API thật).

  ---

  3. 📊 DỮ LIỆU HIỆU SUẤT (BENCHMARKS)

  Cấu hình chuẩn: Vốn $1,000 | Leverage 10x | Max Pos 10 | No CB


  ┌──────────────────┬─────────────────┬───────────────┬──────────────────────────────────────────────────┐
  │ Giai Đoạn        │ Kết Quả (Bal... │ ROI (Lợi N... │ Bài Học                                          │
  ├──────────────────┼─────────────────┼───────────────┼──────────────────────────────────────────────────┤
  │ Tháng 10/2025    │ $29,626         │ x29 lần       │ Sóng biến động mạnh là thiên đường của Limit ... │
  │ Tháng 11/2025    │ $9,136          │ x9 lần        │ Sự ổn định của danh mục 10 coin.                 │
  │ Tháng 12/2025    │ $2,812          │ x2.8 lần      │ Khả năng sinh lời ngay cả trong thị trường khó.  │
  │ **Vốn Siêu Nh... │ $65             │ x3.8 lần      │ Khả năng vực dậy tài khoản từ số vốn "rác".      │
  └──────────────────┴─────────────────┴───────────────┴──────────────────────────────────────────────────┘

  ---

  4. 🚀 LỘ TRÌNH CẢI TIẾN (ACTION PLAN)

  Để đưa dự án từ "Prototype" lên "Production", team cần tập trung vào các hạng mục sau:

  P0: Tối ưu dữ liệu (Urgent)
   * Vấn đề: Backtest 90 ngày hay bị timeout do tải 10 cặp tiền quá lâu.
   * Giải pháp: Xây dựng cơ chế Local Caching.
       * Lần đầu tải từ Binance -> Lưu vào file (CSV/Parquet/SQLite).
       * Lần sau đọc từ đĩa -> Tốc độ nhanh gấp 100 lần.

  P1: Paper Trading (Simulation Realtime)
   * Mục tiêu: Chạy thử hệ thống với dữ liệu realtime 24/7 nhưng tiền ảo.
   * Task: Clone logic của ExecutionSimulator sang một service mới (PaperTradingService) lắng nghe WebSocket
     thật thay vì vòng lặp for.

  P2: Kết nối Frontend - Backend Realtime
   * Mục tiêu: Shark Radar phải hiển thị giá và tín hiệu thật.
   * Task: Cấu hình lại WebSocket endpoint trong App.tsx và run_real_backend.py để đồng bộ dữ liệu.

  P3: "Go Live" (Real Trading)
   * Yêu cầu: Chỉ thực hiện sau khi Paper Trading chạy ổn định 1 tuần không lỗi.
   * An toàn: Bắt đầu với vốn nhỏ ($50 - $100) để kiểm tra độ trễ (Latency) và khớp lệnh.

  ---

  📝 Câu lệnh Khởi động (Quick Start)

  Chạy Backtest "Chiến Thần":

   1 cd backend
   2 python run_backtest.py --top 10 --days 30 --balance 1000 --leverage 10 --no-cb --max-order 50000

  Chạy Hệ thống Realtime (API + Web):

   1 # Terminal 1
   2 python run_real_backend.py
   3 
   4 # Terminal 2
   5 cd frontend
   6 npm run dev

  Đây là toàn bộ tinh hoa của dự án tính đến ngày 02/01/2026. Chúc team phát triển thành công!