# Frontend Architect Context - Current Codebase State

Version: 1.0 | Updated: 2025-12-22
Based on: Actual codebase audit

---

## CODEBASE OVERVIEW

Location: e:\Sach\DuAn\Hinto_Stock\frontend\
Framework: React 19.1.0 + Vite 7.0.4
Styling: TailwindCSS 4.1.17
Desktop: Tauri 2
Charts: Lightweight Charts 5.0.9
Testing: Vitest 2.1.9

---

## DIRECTORY STRUCTURE

```
frontend/
|-- src/
|   |-- App.tsx              # Main app (591 lines, 26KB)
|   |-- App.css              # App styles
|   |-- index.css            # Global styles (4KB)
|   |-- main.tsx             # Entry point
|   |-- components/          # 10 components
|   |-- hooks/               # 2 custom hooks
|   |-- utils/               # Utilities
|   |-- assets/              # Static assets
|   +-- styles/              # Additional styles
|-- src-tauri/               # Tauri desktop config
|-- public/                  # Public assets
|-- package.json             # Dependencies
|-- vite.config.ts           # Vite config
|-- tsconfig.json            # TypeScript config
+-- vitest.config.ts         # Test config
```

---

## COMPONENTS INVENTORY

### Core Trading Components

| Component | File | Size | Description |
|-----------|------|------|-------------|
| CandleChart | CandleChart.tsx | 42KB (977 lines) | Lightweight Charts with VWAP/BB overlays |
| Portfolio | Portfolio.tsx | 15KB | Position management |
| PerformanceDashboard | PerformanceDashboard.tsx | 15KB | Performance metrics |
| Settings | Settings.tsx | 14KB | App settings panel |
| TradeHistory | TradeHistory.tsx | 13KB | Trade log display |
| SignalCard | SignalCard.tsx | 9KB | Signal display card |
| ConnectionStatus | ConnectionStatus.tsx | 6KB | WebSocket status |
| StrategyMonitor | StrategyMonitor.tsx | 4KB | Strategy status |
| PriceTicker | PriceTicker.tsx | 3KB | Live price display |
| SignalLogItem | SignalLogItem.tsx | 1KB | Signal log entry |

### Component Details

#### CandleChart.tsx (Critical - 977 lines)
Features:
- Lightweight Charts integration
- Candlestick series with volume histogram
- VWAP line overlay (yellow #F0B90B)
- Bollinger Bands overlay (blue #2962FF)
- Signal markers (arrows with BUY/SELL)
- Position price lines (entry/SL/TP)
- Timeframe selector (1m, 5m, 15m, 1h, 4h)
- Vietnam timezone conversion
- Auto-resize handling
- History fetch from API

Color Scheme (Binance-style):
```typescript
BINANCE_COLORS = {
  background: '#0B0E11',
  cardBg: '#181A20',
  buy: '#2EBD85',
  sell: '#F6465D',
  vwap: '#F0B90B',
  bollinger: '#2962FF'
}
```

#### SignalCard.tsx
Displays:
- Signal type (BUY/SELL)
- Entry price
- Stop loss
- Take profit
- Confidence score
- Risk/Reward ratio

---

## CUSTOM HOOKS

### useMarketData.ts (10KB, 285 lines)
Purpose: WebSocket connection to backend for real-time data

Features:
- Connects to ws://localhost:8000/ws/market
- Exponential backoff reconnection (1s to 30s cap)
- Parses CANDLE and SIGNAL events
- Returns: data, signal, isConnected, error, reconnectState

Data Structure:
```typescript
interface MarketData {
  open, high, low, close, volume: number;
  timestamp: string;
  vwap?: number;
  bollinger?: { upper_band, lower_band, middle_band };
}

interface Signal {
  type: 'BUY' | 'SELL';
  price, entry_price, stop_loss, take_profit: number;
  confidence, risk_reward_ratio: number;
  timestamp: string;
}
```

### useApi.ts (5KB)
Purpose: REST API calls to backend

---

## APP.TSX STRUCTURE

Main Layout:
```
+------------------------------------------+
|  Header (Status, Connection, Symbol)      |
+------------------------------------------+
|  Tabs: Dashboard | Signals | Portfolio    |
+----------+-------------------------------+
|  Sidebar |  Main Content Area            |
|  (Left)  |  - CandleChart                |
|          |  - SignalCards                |
|          |  - Performance                |
+----------+-------------------------------+
|  Bottom Panel: Trade History             |
+------------------------------------------+
```

State Management:
- useState for local state
- useMarketData hook for WebSocket data
- No external state library (Zustand planned)

Design Tokens (inline):
```typescript
const C = {
  up: '#0ECB81',
  down: '#F6465D',
  yellow: '#F0B90B',
  bg: '#0B0E11',
  card: '#1E2329',
  sidebar: '#09090b',
  border: '#2B3139',
  text1: '#EAECEF',
  text2: '#848E9C',
  text3: '#5E6673'
};
```

---

## TAURI INTEGRATION

Location: src-tauri/
Desktop Features:
- Native window controls
- System tray (planned)
- Local storage
- OS integration

---

## KNOWN ISSUES

| Issue | Severity | Notes |
|-------|----------|-------|
| Signal Panel not updating | Medium | WebSocket event parsing issue |
| Indicator overlays missing | Medium | VWAP/BB not rendered sometimes |

---

## NEXT PRIORITIES

1. **Liquidity Visualization (✅ COMPLETED)**
   - Implement `LiquidityZonePlugin.ts` for Supply/Demand zones
   - Visualize SFP signals with markers (⚡)
   - Update `SignalCard` with Priority UI
2. **Chart UI Polish (✅ COMPLETED)**
   - Custom BBFillPlugin for band fill
   - Binance-style dark theme colors
   - Vietnamese timezone support
3. Add Zustand for state management (✅ Done - `marketStore.ts`)
4. Improve error boundaries

---

## HOW TO RUN

```bash
# Development (web only)
cd frontend
npm run dev

# Development (Tauri desktop)
npm run tauri dev

# Build for production
npm run build
npm run tauri build
```

---

## API ENDPOINTS CONSUMED

| Endpoint | Method | Used By |
|----------|--------|---------|
| /ws/market | WebSocket | useMarketData |
| /market/candles | GET | CandleChart |
| /trades/history | GET | TradeHistory |
| /settings | GET/PUT | Settings |
| / | GET | ConnectionStatus |

---

## DEPENDENCIES

From package.json:
- react: 19.1.0
- react-dom: 19.1.0
- lightweight-charts: 5.0.9
- @tauri-apps/api: 2.x
- tailwindcss: 4.1.17
- vite: 7.0.4
- typescript: 5.8.3
- zustand: 5.0.3 (New)
