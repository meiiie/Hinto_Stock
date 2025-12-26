# Hinto Trader Pro - Frontend

**Professional Desktop Trading UI**

Built with React 18, TypeScript, TradingView Lightweight Charts, and Tauri.

---

## ✨ Features (Dec 2025)

- **📊 Multi-Timeframe Charts** - 1m, 15m, 1h with real-time updates (250ms)
- **🎨 Binance-Style Theme** - Professional dark theme
- **🪙 Token Icons** - @web3icons/react for BTC, ETH, USDT, etc.
- **⚡ State Machine UI** - Visual indicator for trading states
- **📱 Desktop App** - Tauri-powered native application

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Development mode (web)
npm run dev

# Build for production
npm run build

# Desktop app (Tauri)
npm run tauri dev
```

---

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── CandleChart.tsx      # TradingView chart with indicators
│   │   ├── TokenIcon.tsx        # Crypto token icons
│   │   ├── StateIndicator.tsx   # Trading state display
│   │   ├── SignalCard.tsx       # Trade signal cards
│   │   └── ...
│   ├── hooks/
│   │   └── useMarketData.ts     # WebSocket hook (data, data15m, data1h)
│   ├── assets/
│   │   └── icons/               # SVG icon library
│   ├── styles/
│   │   ├── theme.ts             # Design tokens (spacing, sizing, colors)
│   │   └── layout.css           # Utility classes
│   ├── App.tsx                  # Main layout (controlled timeframe)
│   └── main.tsx                 # Entry point
└── src-tauri/                   # Desktop app config
```

---

## 🎨 Theme System

### Spacing (4/8px Grid)
```typescript
THEME.spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48 }
```

### Colors
```typescript
THEME.status.buy   // #0ECB81 (green)
THEME.status.sell  // #F6465D (red)
THEME.accent.yellow // #F0B90B (gold)
```

### Component Sizing
```typescript
THEME.sizing.chart.minHeight  // 400px
THEME.sizing.sidebar.width    // 320px
```

---

## 🔌 WebSocket Integration

### useMarketData Hook

```typescript
const { 
  data,      // 1m realtime candle
  data15m,   // 15m realtime candle (SOTA)
  data1h,    // 1h realtime candle (SOTA)
  isConnected,
  reconnectNow 
} = useMarketData('btcusdt');
```

### Events Handled
- `candle` - 1m tick updates
- `candle_15m` - 15m tick updates (every 250ms)
- `candle_1h` - 1h tick updates (every 250ms)
- `signal` - Trading signals
- `state_change` - State machine transitions

---

## 🪙 Token Icons

Uses `@web3icons/react` with fallback:

```tsx
import { TokenIcon } from './components/TokenIcon';

<TokenIcon symbol="BTC" size={24} />
<TokenIcon symbol="ETH" size={20} />
```

Supported: BTC, ETH, USDT, BNB, SOL (with fallback for others)

---

## 📊 CandleChart Component

### Props
```typescript
interface CandleChartProps {
  timeframe?: '1m' | '15m' | '1h';
  onTimeframeChange?: (tf: Timeframe) => void;
}
```

### Features
- VWAP line (yellow)
- Bollinger Bands (blue)
- Volume histogram
- Entry/SL/TP price lines
- Signal markers

---

## 🔧 Development

### IDE Setup
- VS Code with Tauri + rust-analyzer extensions
- ESLint + Prettier for code formatting

### Scripts
```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run preview  # Preview build
npm run lint     # Run ESLint
```

---

## 📝 License

MIT License
