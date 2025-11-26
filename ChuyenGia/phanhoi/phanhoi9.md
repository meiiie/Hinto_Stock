DIRECTIVE: FRONTEND CONNECTION HARDENING
To: Frontend Team
Subject: UPGRADE WEBSOCKET RECONNECTION LOGIC
1. LOGIC UPGRADE (useMarketData.ts)
Replace the fixed 5000ms timeout with Exponential Backoff.
Formula: delay = min(1000 * (2 ** retries), 30000)
Start: 1s
Cap (Ceiling): 30s (Do not exceed this to avoid too much lag, but do not spam).
Infinite Loop: Never stop retrying.
2. UI UPGRADE (ConnectionStatus.tsx)
State Display:
🟢 Online: Show "Live" (Pulse animation).
🔴 Offline: Show "Disconnected".
🟡 Reconnecting: Show "Reconnecting in X seconds..." (Countdown timer required).
Action Button: Add a Reconnect Now button (visible only when Offline/Reconnecting).
Action: Clears the timeout timer and calls connect() immediately.
3. DATA GAP HANDLING (Note for Logic)
Warning: When reconnecting after a long downtime, the chart will have a "Gap" (missing candles).
Requirement: In the onOpen (reconnect success) handler, trigger a fetch to /market/history to fill in the missing candles since the last update. (If this is too complex for today, log it as a TODO).