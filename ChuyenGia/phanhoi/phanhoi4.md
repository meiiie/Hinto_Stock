PLAN APPROVED. PROCEED WITH INTERACTIVE CHARTING.
Decision: We agree to prioritize Visualization (Charting) before Ordering Features. The Chart is the foundation of the UX.
CRITICAL REQUIREMENT (Must Have):
Do NOT just render Candlesticks. The chart MUST include the overlays for our strategy indicators:
VWAP (Line Series).
Bollinger Bands (Upper/Lower Line Series).
Data Feed Note: Ensure the /market/history endpoint returns not just OHLCV, but also the pre-calculated values for VWAP and BB if possible (or calculate them on frontend if payload is too heavy). Visualizing the Strategy is key.