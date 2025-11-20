# 📊 BÁO CÁO CHI TIẾT HỆ THỐNG 3-LAYER: CRYPTOCURRENCY TRADING PLATFORM

**Project Name:** Hinto Stock AI Trading System
**Version:** 4.0 (Trend Pullback Pivot)
**Date:** November 20, 2025
**Document Owner:** System Architect
**Classification:** Technical Design Specification

---

## 🎯 EXECUTIVE SUMMARY

Hệ thống **Hinto Stock** là nền tảng trading cryptocurrency 24/7 với kiến trúc **3-layer hybrid**.
Sau khi đánh giá kỹ lưỡng và nhận phản hồi từ chuyên gia, dự án đã thực hiện chuyển đổi chiến lược quan trọng (Strategic Pivot) từ **Mean Reversion** sang **Trend Pullback**.

**Strategic Pivot (v4.0):**
- **Old Strategy:** Mean Reversion (RSI < 30). *Problem: High risk, conflicting signals.*
- **New Strategy:** **Trend Pullback** (VWAP + Bollinger Bands + StochRSI). *Advantage: Trade with trend, better R:R.*

**Business Value Proposition:**
- **Professional Logic:** Giao dịch thuận xu hướng (Trend Following) với điểm vào lệnh tối ưu.
- **Smart Entry:** Thuật toán đặt lệnh Limit thông minh để tránh trượt giá và FOMO.
- **Risk-first approach:** Tỷ lệ R:R tối thiểu 1:1.5, bảo toàn vốn là ưu tiên hàng đầu.

**Current Status:** 🔄 **Restructuring Phase** - Updating Layer 1 Core Logic.

---

## 🏗️ 3-LAYER ARCHITECTURE DESIGN

### 🌐 System Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                       │
│                     (Streamlit Dashboard + Mobile App)              │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Layer 3     │  │ Layer 2     │  │ Layer 1     │  │ Risk        │  │
│  │ LLM Planner │  │ Candle      │  │ Real-time   │  │ Management  │  │
│  │ (30m-1h)    │  │ Confirmer   │  │ Signals     │  │ System      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                            DOMAIN LAYER                             │
│  (Entities, Value Objects, Domain Services, Repository Interfaces)  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                         │
│  (Binance API, SQLite DB, WebSocket, TA-Lib, DI Container, Logging) │
└─────────────────────────────────────────────────────────────────────┘
```

### 🔍 Layer 1: Real-time Trading Signals (Trend Pullback Core)

#### **Core Strategy: Trend Pullback**
Thay vì bắt đáy khi giá rơi mạnh, hệ thống sẽ đợi xu hướng tăng được xác nhận và mua khi giá điều chỉnh nhẹ (Pullback).

#### **Technical Specifications**
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Trend Filter** | **VWAP** (Volume Weighted Average Price) | Xác định xu hướng chính & Hỗ trợ cứng. |
| **Volatility** | **Bollinger Bands** (20, 2) | Đo biến động, xác định vùng quá mua/bán tương đối. |
| **Trigger** | **StochRSI** (3, 3, 14, 14) | Tín hiệu vào lệnh chính xác từng nến. |
| **Confirmation** | **Volume** + Candle Color | Xác nhận dòng tiền tham gia. |

#### **Signal Logic (Simplified)**
1.  **BUY Signal:**
    *   Price > VWAP (Uptrend).
    *   Price touches Lower Bollinger Band or VWAP (Pullback).
    *   StochRSI crosses above 20 (Momentum shift).
    *   Volume > Previous Red Candle (Buying pressure).
2.  **SELL Signal:**
    *   Price < VWAP (Downtrend).
    *   Price touches Upper Bollinger Band or VWAP (Rally).
    *   StochRSI crosses below 80.

#### **Smart Entry Algorithm**
*   **No Market Orders:** Không bao giờ mua ngay giá đóng cửa.
*   **Limit Order:** Đặt lệnh Limit thấp hơn giá đóng cửa (cho Buy) dựa trên độ dài thân nến.
    *   Formula: `Entry = Close - (Body_Size * Pullback_Ratio)`
    *   Ratio: 0.3 - 0.5 tùy vào lực nến.

---

### 🔍 Layer 2: Candle Confirmation Strategy (Signal Enhancement)

#### **Architecture & Responsibilities**
*   **Latency target:** 2-5 minutes
*   **Update frequency:** Per candle close
*   **Focus:** Xác nhận tín hiệu Layer 1 bằng mô hình nến đảo chiều.

#### **Professional Trading Patterns**
| Pattern | Conditions | Success Rate |
|---------|------------|--------------|
| **Bullish Engulfing** | Nến xanh bao trùm nến đỏ trước đó tại vùng hỗ trợ (VWAP/Lower BB). | High |
| **Pin Bar (Hammer)** | Râu nến dưới dài, từ chối giá giảm tại hỗ trợ. | High |
| **Inside Bar Breakout** | Nến nhỏ nằm trong nến trước, phá vỡ theo xu hướng. | Medium |

---

### 🔍 Layer 3: LLM Strategic Planning (Long-term Strategy)

#### **Architecture & Responsibilities**
*   **Latency target:** 10-30 minutes
*   **Focus:** Phân tích bối cảnh thị trường rộng hơn (Market Regime) và quản lý tâm lý/rủi ro vĩ mô.

#### **LLM Role**
*   Phân tích tin tức và sự kiện kinh tế (nếu tích hợp data feed).
*   Đánh giá cấu trúc thị trường (Market Structure) trên khung H1/H4.
*   Điều chỉnh Risk Profile (Aggressive/Conservative) dựa trên biến động thị trường.

---

## 🔧 TECHNICAL IMPLEMENTATION DETAILS

### 📦 Project Structure Enhancement
(Giữ nguyên cấu trúc Clean Architecture hiện tại, cập nhật các Service bên trong)

### ⚙️ Critical Integration Points
*   **Signal Generator:** Refactor để sử dụng VWAP/StochRSI thay vì EMA/RSI thuần.
*   **Entry Calculator:** Implement `SmartEntry` logic.
*   **Risk Manager:** Cập nhật logic Stoploss theo Swing Low/High thay vì ATR.

---

## 📊 PERFORMANCE METRICS & TARGETS

### 🎯 Success Metrics (v4.0)
| Metric | Target | Rationale |
|--------|--------|-----------|
| **Win Rate** | > 55% | Trend Following thường có Winrate thấp hơn Mean Reversion nhưng Profit cao hơn. |
| **Risk/Reward** | > 1:1.5 | Lợi nhuận trung bình phải lớn hơn 1.5 lần rủi ro. |
| **Drawdown** | < 15% | Kiểm soát rủi ro chặt chẽ. |
| **Profit Factor** | > 1.5 | Tổng thắng / Tổng thua. |

---

## 🗓️ IMPLEMENTATION ROADMAP (REVISED)

### 📋 Phase 1: Restructuring Layer 1 (Current Week)
| Task | Priority | Status |
|------|----------|--------|
| **Install VWAP/StochRSI libs** | 🔴 HIGH | Pending |
| **Refactor Signal Logic** | 🔴 HIGH | Pending |
| **Implement Smart Entry** | 🔴 HIGH | Pending |
| **Update Risk Manager** | 🔴 HIGH | Pending |
| **Backtest Validation (30 days)** | 🔴 HIGH | Pending |

### 📋 Phase 2: Dashboard & Visualization (Next Week)
| Task | Priority | Status |
|------|----------|--------|
| **Add VWAP/BB to Charts** | 🟡 MEDIUM | Pending |
| **Visualize Entry/SL/TP** | 🟡 MEDIUM | Pending |
| **Real-time Signals Panel** | 🟡 MEDIUM | Pending |

### 📋 Phase 3: Layer 2 & 3 (Future)
*   Triển khai sau khi Layer 1 ổn định và đạt target lợi nhuận.

---

## 🔚 CONCLUSION

Việc chuyển đổi sang **Trend Pullback** là bước đi cần thiết để đưa hệ thống từ "thử nghiệm" sang "chuyên nghiệp". Chúng ta loại bỏ các chỉ báo xung đột và tập trung vào bản chất của trading: **Xu hướng và Dòng tiền**.

**Immediate Action:** Thực hiện kế hoạch tái cấu trúc kỹ thuật (Technical Restructuring Plan) ngay lập tức.