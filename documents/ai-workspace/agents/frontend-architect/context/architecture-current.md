# 📐 UI ARCHITECTURE CURRENT STATE

**Last Updated:** 2025-12-22
**Owner:** Frontend Architect

---

## CURRENT STACK

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.x |
| Build | Vite | 5.x |
| Desktop | Electron | TBD |
| Styling | TailwindCSS | 3.x |
| State | TBD (Zustand recommended) | - |
| Charts | Lightweight Charts | 4.x |
| Icons | Lucide React | - |

---

## PAGE STRUCTURE

```
📁 src/
├── 📁 pages/
│   ├── Dashboard.tsx        # Main trading dashboard
│   ├── Settings.tsx         # App settings
│   └── History.tsx          # Trade history
│
├── 📁 components/
│   ├── 📁 ui/               # Atomic components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   │
│   ├── 📁 trading/          # Domain components
│   │   ├── CandleChart.tsx  # 🔴 Needs VWAP/BB overlay
│   │   ├── SignalPanel.tsx  # 🔴 Needs real-time signals
│   │   ├── OrderForm.tsx
│   │   └── PositionList.tsx
│   │
│   └── 📁 layout/           # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── DashboardLayout.tsx
│
├── 📁 hooks/                # Custom hooks
│   ├── useWebSocket.ts
│   └── useSignals.ts
│
├── 📁 stores/               # State management
│   └── signalStore.ts
│
└── 📁 services/             # API services
    └── api.ts
```

---

## COMPONENT STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| CandleChart | 🟡 Partial | Missing VWAP/BB overlays |
| SignalPanel | 🔴 Not Working | Event bus integration broken |
| OrderForm | 🟡 Partial | Needs API connection |
| PositionList | 🟡 Partial | Needs real-time updates |
| Settings | 🟢 Done | Basic functionality |

---

## KNOWN ISSUES

1. **Signal Panel Not Updating**
   - EventBus not properly connected
   - Need to verify backend → frontend communication

2. **Chart Overlays Missing**
   - VWAP needs to be calculated and displayed
   - Bollinger Bands need implementation

3. **State Management**
   - Currently ad-hoc, needs consolidation
   - Recommend Zustand for simplicity

---

## DESIGN TOKENS (TBD)

```css
/* Colors */
--color-bullish: #22c55e;  /* Green for long/buy */
--color-bearish: #ef4444;  /* Red for short/sell */
--color-neutral: #6b7280;  /* Gray for neutral */

/* Trading specific */
--color-take-profit: #22c55e;
--color-stop-loss: #ef4444;
--color-entry: #3b82f6;

/* Background */
--bg-primary: #0f172a;     /* Dark slate */
--bg-secondary: #1e293b;
--bg-card: #334155;
```

---

## NEXT STEPS

1. [ ] Integrate EventBus for real-time signals
2. [ ] Add VWAP/BB overlays to chart
3. [ ] Connect OrderForm to Backend API
4. [ ] Implement proper state management
5. [ ] Dark mode polishing

---

**Update When:** Major UI changes or architecture decisions
