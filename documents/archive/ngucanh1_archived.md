PROJECT CONTEXT SUMMARY: HINTO STOCK
Date: 2025-11-22 Version: 2.1 (Optimized Trend Pullback) Status: Pre-Production / Final Simulation Phase

1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)
Hinto_Stock là một hệ thống giao dịch tự động (Trading Bot) được xây dựng theo kiến trúc Clean Architecture (Python).

Mục tiêu: Tạo ra lợi nhuận ổn định từ thị trường Crypto (BTCUSDT) thông qua giao dịch thuật toán.
Mô hình: USDT-M Futures (Isolated 1x Leverage - An toàn là trên hết).
Giao diện: Streamlit Dashboard (Realtime monitoring & Paper Trading).
2. HÀNH TRÌNH & GIAI ĐOẠN (PROJECT JOURNEY)
✅ Các Giai Đoạn Đã Hoàn Thành (Completed Phases)
Phase 1-12 (Foundation): Xây dựng Core Backend, Data Pipeline (WebSocket), Dashboard hiển thị, và hệ thống Paper Trading cơ bản.
Phase 13 (Pivot to Futures): Chuyển đổi từ Spot sang Futures Model (Short Selling, Margin, PnL tính theo Mark Price).
Phase 14 (Simulation Tuning): Bắt đầu chạy giả lập (Simulation) để kiểm chứng chiến thuật.
Phase 15 (Strategy Correction):
Sự cố: Phát hiện chiến thuật cũ (RSI Counter-trend) bị sai lầm nghiêm trọng (Lỗ 30%).
Khắc phục: Chuyển sang chiến thuật Trend Pullback (Thuận xu hướng) theo chỉ đạo của Chuyên gia.
Phase 16 (Real Data Test):
Tải dữ liệu thật từ Binance.
Chạy Simulation trên 1000 nến (10 ngày). Kết quả ban đầu lỗ nhẹ (-1.89%) do bộ lọc quá lỏng lẻo.
🚀 Giai Đoạn Hiện Tại (Current Phase)
Phase 17: Final Optimization & Simulation Chúng ta đang ở bước cuối cùng trước khi "Go Live" (Burn-in Test).

Mục tiêu: Tinh chỉnh bộ lọc để biến PnL từ Âm sang Dương trên dữ liệu lịch sử dài hạn (3 tháng).
Trạng thái:
Đã cập nhật logic 
SignalGenerator
 với các bộ lọc mới (Strict R:R, Volume Climax, ADX).
Đã tải 3 tháng dữ liệu (8640 nến).
Đang chuẩn bị chạy Simulation 3 tháng.
3. CHIẾN THUẬT GIAO DỊCH (MASTER STRATEGY)
Tên gọi: Hinto Trend Pullback (Layer 1) Khung thời gian: 15 Phút (15m)

A. Tư Duy Cốt Lõi (Core Philosophy)
"Trend is King". Không bao giờ chặn đầu xe lửa. Chỉ đánh thuận theo xu hướng chủ đạo được xác định bởi dòng tiền (VWAP).

B. Logic Chi Tiết (Technical Logic)
Trend Filter (Bộ lọc Xu hướng):

Dùng VWAP (Volume Weighted Average Price).
Price > VWAP -> UPTREND (Chỉ tìm lệnh BUY).
Price < VWAP -> DOWNTREND (Chỉ tìm lệnh SELL).
Entry Setup (Điểm vào lệnh):

BUY: Giá hồi về (Pullback) chạm Lower Bollinger Band hoặc VWAP.
SELL: Giá hồi lên (Rally) chạm Upper Bollinger Band hoặc VWAP.
Trigger (Kích hoạt):

StochRSI (14, 14, 3, 3):
Buy: Cắt lên trên mức 30.
Sell: Cắt xuống dưới mức 70.
Confirmation: Nến đảo chiều (Xanh cho Buy, Đỏ cho Sell) + Volume ủng hộ.
Advanced Filters (Bộ lọc Nâng cao - Mới thêm):

Strict R:R: Nếu (TP1 - Entry) / (Entry - SL) < 1.0 -> HUỶ LỆNH. (Không đánh đổi rủi ro cao lấy lợi nhuận thấp).
Volume Climax: Nếu Volume > 4.0x trung bình -> HUỶ LỆNH. (Tránh bắt dao rơi/đỉnh cao trào).
ADX Filter: Nếu ADX < 20 -> HUỶ LỆNH. (Tránh thị trường đi ngang/Sideway).
4. TRẠNG THÁI KỸ THUẬT (TECHNICAL STATE)
📂 File Quan Trọng
src/application/signals/signal_generator.py
: Chứa toàn bộ logic chiến thuật và bộ lọc nêu trên. Lưu ý: File này đang có lỗi cú pháp ở dòng cuối cùng (do thao tác thừa), cần xóa đi.
scripts/fetch_data.py
: Script tải dữ liệu lịch sử (đã tải xong 3 tháng).
scripts/run_simulation.py
: Script chạy giả lập (đã trỏ vào 
SignalGenerator
 thật).
📊 Dữ Liệu
data/btc_15m.csv
: Chứa 8640 nến (3 tháng) dữ liệu thật từ Binance.
5. NHIỆM VỤ TIẾP THEO (NEXT ACTION ITEMS)
Sửa lỗi Code: Vào 
src/application/signals/signal_generator.py
, xóa đoạn code rác ở cuối file.
Chạy Simulation: Thực thi lệnh python scripts/run_simulation.py để chạy test trên 3 tháng dữ liệu.
Báo Cáo & Đánh Giá:
Đọc file kết quả trong thư mục reports/.
Nếu PnL > 0 và số lượng lệnh hợp lý (> 30 lệnh/3 tháng) -> Thành công.
Nếu PnL < 0 -> Phân tích log để tìm nguyên nhân (thường do Stoploss quá chặt hoặc dính nhiễu).
Đây là toàn bộ bối cảnh cần thiết để tiếp tục dự án một cách liền mạch. Hãy bám sát "Master Strategy" và không tự ý thay đổi logic cốt lõi.