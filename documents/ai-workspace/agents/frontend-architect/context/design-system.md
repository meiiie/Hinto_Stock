# 🎨 DESIGN SYSTEM - Hinto Stock Trading

**Last Updated:** 2025-12-22
**Owner:** Frontend Architect

---

## 1. COLOR PALETTE

### Trading Colors (Non-negotiable)
| Name | Hex | Usage |
|------|-----|-------|
| Bullish/Long | `#22c55e` | Buy signals, profit, uptrend |
| Bearish/Short | `#ef4444` | Sell signals, loss, downtrend |
| Neutral | `#6b7280` | No signal, sideways |
| Warning | `#f59e0b` | Caution, risk alerts |
| Info | `#3b82f6` | Entry points, information |

### Background (Dark Theme)
| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#0f172a` | Main background |
| Secondary | `#1e293b` | Card backgrounds |
| Tertiary | `#334155` | Elevated surfaces |
| Border | `#475569` | Subtle borders |

### Text
| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#f8fafc` | Main text |
| Secondary | `#94a3b8` | Muted text |
| Disabled | `#64748b` | Inactive text |

---

## 2. TYPOGRAPHY

### Font Stack
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Scale
| Name | Size | Weight | Usage |
|------|------|--------|-------|
| Display | 2rem | 700 | Dashboard titles |
| H1 | 1.5rem | 600 | Section headers |
| H2 | 1.25rem | 600 | Card titles |
| H3 | 1rem | 500 | Subsections |
| Body | 0.875rem | 400 | General text |
| Small | 0.75rem | 400 | Captions, labels |
| Mono | 0.875rem | 400 | Prices, numbers |

### Number Display
```css
/* Always use tabular numbers for trading data */
.price, .number {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}
```

---

## 3. SPACING

### Base
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.5rem;    /* 24px */
--space-6: 2rem;      /* 32px */
--space-8: 3rem;      /* 48px */
```

### Component Spacing
| Component | Padding | Gap |
|-----------|---------|-----|
| Card | `--space-4` | `--space-3` |
| Button | `--space-2 --space-4` | - |
| Input | `--space-2 --space-3` | - |
| Panel | `--space-4` | `--space-4` |

---

## 4. COMPONENTS

### Buttons
```css
/* Primary Action (e.g., Place Order) */
.btn-primary {
  background: var(--color-info);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

/* Long/Buy */
.btn-long {
  background: var(--color-bullish);
}

/* Short/Sell */
.btn-short {
  background: var(--color-bearish);
}
```

### Cards
```css
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 1rem;
}
```

### Input Fields
```css
.input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
}

.input:focus {
  border-color: var(--color-info);
  outline: none;
}
```

---

## 5. TRADING-SPECIFIC PATTERNS

### Price Display
```jsx
// Always show direction indicator
<span className={`price ${change >= 0 ? 'text-bullish' : 'text-bearish'}`}>
  {change >= 0 ? '▲' : '▼'} {price.toFixed(2)}
</span>
```

### Signal Badge
```jsx
<div className={`badge badge-${direction.toLowerCase()}`}>
  {direction} {symbol}
</div>
```

### Entry/SL/TP Lines
| Type | Color | Line Style |
|------|-------|------------|
| Entry | `#3b82f6` | Solid |
| Stop Loss | `#ef4444` | Dashed |
| Take Profit | `#22c55e` | Dashed |

---

## 6. ANIMATION

### Transitions
```css
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
--transition-slow: 350ms ease;
```

### Price Updates
```css
/* Flash on price update */
.price-update-up {
  animation: flash-green 0.3s ease;
}

.price-update-down {
  animation: flash-red 0.3s ease;
}

@keyframes flash-green {
  0% { background: rgba(34, 197, 94, 0.3); }
  100% { background: transparent; }
}
```

---

## 7. RESPONSIVE BREAKPOINTS

| Name | Width | Description |
|------|-------|-------------|
| Desktop | 1280px+ | Full dashboard |
| Desktop SM | 1024px | Compact layout |
| Tablet | 768px | Stack panels |
| Mobile | 640px | Not primary target |

---

## 8. ACCESSIBILITY

### Minimum Requirements
- Color contrast: 4.5:1 for normal text
- Focus indicators on all interactive elements
- Keyboard navigation support
- Screen reader labels for trading actions

### Color-blind Considerations
- Don't rely solely on red/green
- Add icons or patterns for signals
- Use position (up arrow/down arrow) as additional indicator

---

## 9. ICONS

### Trading Icons (from Lucide)
| Icon | Usage |
|------|-------|
| `TrendingUp` | Long/Buy signal |
| `TrendingDown` | Short/Sell signal |
| `AlertTriangle` | Risk alert |
| `DollarSign` | Price, balance |
| `Activity` | Market activity |
| `BarChart2` | Charts |
| `Settings` | Settings |

---

**Usage:** All UI components MUST reference this design system. No ad-hoc styles.
