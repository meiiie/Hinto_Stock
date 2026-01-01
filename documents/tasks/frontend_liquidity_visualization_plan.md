# Frontend Upgrade Plan: Liquidity & SFP Visualization

**Status:** Draft
**Target:** Frontend Team / AI Frontend Architect
**Objective:** Visualize "Invisible" Institutional Data (Liquidity Zones, SFP) on the Chart.

---

## 1. Context & Motivation
The Backend has been upgraded with Institutional Grade algorithms (v2.3):
- **Liquidity Zones:** Estimated areas of Stop Loss clusters.
- **SFP (Swing Failure Pattern):** Zero-lag reversal signals.
- **Signal Priority:** HIGH (SFP) vs MEDIUM (Pullback).

**Problem:** The Frontend currently is "blind" to these features. It only shows standard candles. Users need to SEE the zones to trust the trade.

---

## 2. Feature Requirements

### Feature A: Liquidity Zones Layer (The "Kill Zones")
**Concept:** Draw semi-transparent rectangles extending from Swing Highs/Lows into the future.
- **Red Zone (Supply/Resistance):** Above Swing Highs. "Take Profit here."
- **Green Zone (Demand/Support):** Below Swing Lows. "Watch for SFP buy here."

**Technical Implementation:**
- Use `lightweight-charts` custom primitive or series of Box/Rectangles.
- **Data Source:** Backend needs to broadcast `liquidity_zones` via WebSocket (EventBus).
- **Visuals:**
  - `Stop Loss Clusters` (Below price): Color `rgba(255, 82, 82, 0.15)` (Red tint).
  - `Take Profit Zones` (Above price): Color `rgba(0, 150, 136, 0.15)` (Green tint).
  - Zones should extend to the right edge of the chart (infinite timeline).

### Feature B: SFP Markers (The "Lightning Strike")
**Concept:** Mark the specific candle that swept liquidity and reversed.
**Technical Implementation:**
- Use `lightweight-charts` **Markers** API.
- **Icon:** Use a Lightning Bolt (⚡) or Arrow.
- **Position:** 
  - Bullish SFP: Below the candle Low.
  - Bearish SFP: Above the candle High.
- **Tooltip:** Hovering shows "SFP: Zero Lag Entry".

### Feature C: Signal Priority UI
**Concept:** Differentiate between a "Wait for pullback" signal and a "BUY NOW" signal.
**Technical Implementation:**
- **High Priority (SFP):** 
  - Card Border: Gold/Yellow glow.
  - Badge: "URGENT" or "INSTANT".
- **Medium Priority (Pullback):**
  - Standard styling.

---

## 3. Implementation Steps

### Step 1: Backend Data Exposure (Backend Task)
- Ensure `RealtimeService` broadcasts the `LiquidityZonesResult` in the WebSocket payload.
- Currently, it might only be internal. We need to add it to the `candle_update` event or a separate `analysis_update` event.

### Step 2: Custom Chart Plugin (Frontend Task)
- Create `src/components/Chart/plugins/LiquidityZonePlugin.ts`.
- This plugin will receive the Zone coordinates (Price High, Price Low, Start Time) and render rectangles using Canvas rendering context.

### Step 3: Integrate with Store
- Update `useMarketData` to parse the new WebSocket message types.
- Store zones in `useStore`.

---

## 4. Why this matters (User Value)
- **Trust:** When the bot buys at a "random" low, the user might be scared. If they see the Green Zone there, they understand: *"Ah, it's hunting stop losses. Good bot."*
- **Education:** Teaches the user to see the market like a Market Maker.

---
*Plan created by Quant Specialist AI - Dec 31, 2025*
