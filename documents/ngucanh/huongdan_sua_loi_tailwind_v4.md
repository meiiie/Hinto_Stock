# Hướng Dẫn Sửa Lỗi Tailwind CSS v4 Không Nhận Layout

## Vấn Đề

Khi sử dụng Tailwind CSS v4 với Vite, các class CSS như `text-[10px]`, `gap-8`, `w-80` không được áp dụng đúng cách. Layout bị vỡ, text không đúng kích thước, spacing không hoạt động.

## Nguyên Nhân

1. **Tailwind v4 thay đổi cách hoạt động**: Sử dụng `@theme` directive thay vì `tailwind.config.js`
2. **Vite cache**: Cache cũ giữ lại CSS đã compile
3. **CSS specificity**: Inline styles có độ ưu tiên cao hơn Tailwind classes
4. **HMR không đồng bộ**: Hot Module Replacement không cập nhật đúng

## Giải Pháp: Sử Dụng Inline Styles

### Nguyên Tắc Chính

**Thay vì dùng Tailwind classes:**
```tsx
// ❌ KHÔNG ỔN ĐỊNH với Tailwind v4
<div className="flex items-center gap-8 text-[10px] font-bold">
```

**Sử dụng inline styles:**
```tsx
// ✅ LUÔN HOẠT ĐỘNG
<div style={{
  display: 'flex',
  alignItems: 'center',
  gap: '32px',
  fontSize: '10px',
  fontWeight: 700,
}}>
```

### Bảng Chuyển Đổi Tailwind → Inline Styles

| Tailwind Class | Inline Style |
|----------------|--------------|
| `flex` | `display: 'flex'` |
| `flex-col` | `flexDirection: 'column'` |
| `items-center` | `alignItems: 'center'` |
| `justify-between` | `justifyContent: 'space-between'` |
| `gap-4` | `gap: '16px'` |
| `gap-8` | `gap: '32px'` |
| `w-80` | `width: '320px'` |
| `h-12` | `height: '48px'` |
| `p-4` | `padding: '16px'` |
| `px-4` | `padding: '0 16px'` |
| `py-2` | `padding: '8px 0'` |
| `text-[10px]` | `fontSize: '10px'` |
| `text-xs` | `fontSize: '12px'` |
| `text-sm` | `fontSize: '14px'` |
| `text-lg` | `fontSize: '18px'` |
| `text-xl` | `fontSize: '20px'` |
| `font-bold` | `fontWeight: 700` |
| `font-medium` | `fontWeight: 500` |
| `tracking-wider` | `letterSpacing: '0.05em'` |
| `uppercase` | `textTransform: 'uppercase'` |
| `rounded` | `borderRadius: '4px'` |
| `rounded-md` | `borderRadius: '6px'` |
| `rounded-full` | `borderRadius: '50%'` |
| `overflow-hidden` | `overflow: 'hidden'` |
| `flex-shrink-0` | `flexShrink: 0` |
| `min-h-0` | `minHeight: 0` |
| `border-b` | `borderBottom: '1px solid #color'` |

### Ví Dụ Thực Tế

#### Component Trước (Tailwind classes)
```tsx
const SignalLogItem = ({ time, action, trend }) => {
  return (
    <div className="flex items-center gap-1 py-1 border-b border-zinc-800/50 text-[10px]">
      <span className="w-14 shrink-0 font-mono text-zinc-500">{time}</span>
      <span className="w-10 shrink-0 font-semibold text-zinc-400">{action}</span>
      <span className="flex-1 text-right font-bold">{trend}</span>
    </div>
  );
};
```

#### Component Sau (Inline styles)
```tsx
const SignalLogItem = ({ time, action, trend }) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '4px 0',
      borderBottom: '1px solid rgba(39,39,42,0.5)',
      fontSize: '10px',
      fontFamily: "'JetBrains Mono', monospace",
      minHeight: '20px',
    }}>
      <span style={{ width: '60px', flexShrink: 0, color: '#71717a' }}>{time}</span>
      <span style={{ width: '40px', flexShrink: 0, color: '#a1a1aa', fontWeight: 600 }}>{action}</span>
      <span style={{ flex: 1, textAlign: 'right', fontWeight: 700 }}>{trend}</span>
    </div>
  );
};
```

### Design Tokens Pattern

Tạo object chứa tất cả màu sắc và giá trị thiết kế:

```tsx
// Design tokens - đặt ở đầu file
const C = {
  // Trading colors
  up: '#0ECB81',      // Green - tăng
  down: '#F6465D',    // Red - giảm
  yellow: '#F0B90B',  // Accent
  
  // Backgrounds
  bg: '#0B0E11',      // Main background
  card: '#1E2329',    // Card background
  sidebar: '#09090b', // Sidebar (darker)
  border: '#2B3139',  // Border color
  
  // Text hierarchy
  text1: '#EAECEF',   // Primary text
  text2: '#848E9C',   // Secondary text
  text3: '#5E6673',   // Muted text
};

// Sử dụng
<div style={{ backgroundColor: C.card, color: C.text1, borderBottom: `1px solid ${C.border}` }}>
```

## Các Bước Xử Lý Khi Gặp Lỗi

### 1. Xóa Cache Vite
```bash
cd frontend
Remove-Item -Recurse -Force node_modules/.vite, dist -ErrorAction SilentlyContinue
npm run dev
```

### 2. Hard Refresh Browser
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`
- Hoặc mở DevTools → Network → Check "Disable cache"

### 3. Kiểm Tra Trong Incognito Mode
Mở trang trong cửa sổ ẩn danh để loại bỏ cache browser

### 4. Chuyển Sang Inline Styles
Nếu vẫn không hoạt động, chuyển component sang inline styles như hướng dẫn trên

## Khi Nào Dùng Tailwind vs Inline Styles

| Tình huống | Khuyến nghị |
|------------|-------------|
| Layout phức tạp, cần chính xác | Inline styles |
| Fixed-width columns | Inline styles |
| Dynamic colors dựa trên state | Inline styles |
| Responsive design đơn giản | Tailwind classes |
| Utility classes cơ bản | Tailwind classes |

## Lưu Ý Quan Trọng

1. **Inline styles có độ ưu tiên cao nhất** - luôn override Tailwind
2. **Không cần restart Vite** khi thay đổi inline styles
3. **Dễ debug hơn** - có thể inspect trực tiếp trong DevTools
4. **Performance tương đương** - React tối ưu hóa inline styles

## Files Đã Sửa Trong Dự Án

- `frontend/src/App.tsx` - Main layout với inline styles
- `frontend/src/components/SignalLogItem.tsx` - Fixed-width columns
- `frontend/src/components/StrategyMonitor.tsx` - Progress bars và indicators
- `frontend/src/components/CandleChart.tsx` - Chart header, ticker bar, tooltips

## Xử Lý Giá Trị "---" Khi Chưa Có Data

Khi data chưa load xong, giá trị có thể là 0 hoặc undefined. Cần kiểm tra trước khi hiển thị:

```tsx
// ❌ SAI - Hiển thị "---" khi price = 0
<span>${formatPrice(currentPrice)}</span>

// ✅ ĐÚNG - Kiểm tra trước khi hiển thị
<span>{currentPrice > 0 ? `$${formatPrice(currentPrice)}` : '---'}</span>

// Với price change
<span>
  {currentPrice > 0 
    ? `${priceChange >= 0 ? '+' : ''}${formatPrice(priceChange)} (${((priceChange / currentPrice) * 100).toFixed(2)}%)`
    : '---'
  }
</span>
```

---

*Tài liệu này được tạo ngày 25/11/2025 sau khi xử lý lỗi Tailwind v4 không nhận layout trong dự án Hinto Trading Dashboard.*
