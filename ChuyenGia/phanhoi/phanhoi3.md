PLAN APPROVED. EXECUTE PHASE 6.2 (WEBSOCKETS).
Critical Technical Constraints:
Non-blocking Startup: In main.py lifespan, ensure realtime_service.start() is wrapped in asyncio.create_task(). Do NOT await the infinite loop directly, or the API will hang.
Data Bridge: Implement a lightweight Pub/Sub pattern (using asyncio.Queue or List of Callbacks) to bridge data from the Trading Engine to the WebSocket endpoint.
Error Handling: Handle WebSocketDisconnect gracefully. Do not let the server crash if the Frontend is closed abruptly.
Goal: Even if the Frontend connects/disconnects 100 times, the Backend Trading Engine must keep running without interruption.