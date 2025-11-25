PLAN ADJUSTED. SIMPLIFY THE IMPLEMENTATION.
Architectural Directive:
Backend Stability: Do NOT complicate the RealtimeService broadcast logic. Keep streaming the 1m Candle (Atomic Update) via WebSocket.
Client-Side Logic: The Frontend is responsible for updating the 15m/1h chart based on the incoming 1m data stream.
Logic: If viewing 15M chart, when a 1M update arrives -> Update the current forming 15M candle (update High/Low/Close). Do not ask Backend for specific 15m streams.
Product Requirement:
Default View: The App MUST open directly to the 15M Timeframe (Since this is our Strategy's timeframe).
Selector: You can add 1H for reference, but 1M is low priority (too much noise).
Goal: Fast implementation on Frontend, Zero risk on Backend.