(.venv) E:\Sach\DuAn\Hinto_Stock>python e:\Sach\DuAn\Hinto_Stock\run_real_backend.py
🚀 Starting Hinto Trading Dashboard - Real Backend
📡 Connecting to Binance WebSocket...
==================================================
INFO:     Started server process [11716]
INFO:     Waiting for application startup.
2025-12-26 19:09:40,362 - src.api.main - INFO - 🚀 Starting up Hinto Trader Pro API...
2025-12-26 19:09:40,362 - src.api.event_bus - INFO - EventBus initialized
2025-12-26 19:09:40,363 - src.api.websocket_manager - INFO - WebSocketManager initialized
2025-12-26 19:09:40,363 - src.infrastructure.indicators.talib_calculator - INFO - Using TA-Lib version 0.6.8
2025-12-26 19:09:40,363 - src.infrastructure.indicators.atr_calculator - INFO - ATRCalculator initialized with period=14    
2025-12-26 19:09:40,363 - src.infrastructure.indicators.adx_calculator - INFO - ADXCalculator initialized with period=14    
2025-12-26 19:09:40,363 - src.infrastructure.indicators.atr_calculator - INFO - ATRCalculator initialized with period=14    
2025-12-26 19:09:40,363 - src.infrastructure.indicators.volume_spike_detector - INFO - VolumeSpikeDetector initialized with threshold=2.0x
2025-12-26 19:09:40,364 - src.application.services.tp_calculator - INFO - TPCalculator initialized: min_RR=1.5, tp3_ext=1.500%
2025-12-26 19:09:40,364 - src.application.services.stop_loss_calculator - INFO - StopLossCalculator initialized: max_risk=1.000%, min_distance=0.300%
2025-12-26 19:09:40,364 - src.application.services.confidence_calculator - INFO - ConfidenceCalculator initialized
2025-12-26 19:09:40,368 - src.application.analysis.rsi_monitor - INFO - RSIMonitor initialized: period=6, thresholds=[20.0, 35.0, 65.0, 80.0]
2025-12-26 19:09:40,368 - src.application.services.entry_price_calculator - INFO - EntryPriceCalculator initialized: offset=0.100%, max_ema_distance=0.500%
2025-12-26 19:09:40,368 - src.application.services.tp_calculator - INFO - TPCalculator initialized: min_RR=1.5, tp3_ext=1.500%
2025-12-26 19:09:40,368 - src.application.services.stop_loss_calculator - INFO - StopLossCalculator initialized: max_risk=1.000%, min_distance=0.300%
2025-12-26 19:09:40,368 - src.application.services.confidence_calculator - INFO - ConfidenceCalculator initialized
2025-12-26 19:09:40,369 - src.infrastructure.di_container - INFO - Created RealtimeService for btcusdt with all dependencies
2025-12-26 19:09:40,370 - src.application.services.data_retention_service - INFO - 📦 DataRetentionService initialized: 1m=7d, 15m=30d, 1h=90d
2025-12-26 19:09:40,370 - src.api.event_bus - INFO - EventBus captured event loop: <ProactorEventLoop running=True closed=False debug=False>
2025-12-26 19:09:40,370 - src.api.event_bus - INFO - 🚀 Broadcast Worker Started (Thread-Safe Mode)
2025-12-26 19:09:40,371 - src.api.main - INFO - ✅ EventBus broadcast worker started
2025-12-26 19:09:40,371 - src.application.services.realtime_service - INFO - ✅ EventBus connected to RealtimeService       
2025-12-26 19:09:40,371 - src.api.main - INFO - ✅ EventBus connected to RealtimeService
2025-12-26 19:09:40,371 - src.api.main - INFO - ✅ RealtimeService starting...
2025-12-26 19:09:40,371 - src.application.services.data_retention_service - INFO - 🧹 DataRetentionService started
2025-12-26 19:09:40,371 - src.api.main - INFO - ✅ DataRetentionService started (auto-cleanup enabled)
2025-12-26 19:09:40,372 - src.application.services.realtime_service - INFO - Starting real-time service for btcusdt
2025-12-26 19:09:40,372 - src.application.services.realtime_service - INFO - Loading historical data...
2025-12-26 19:09:40,372 - src.application.services.realtime_service - INFO - 🚀 Loading historical candles (SOTA Hybrid)... 
2025-12-26 19:09:40,377 - src.application.services.realtime_service - INFO - 📦 SQLite HIT: 500/500 1m candles
2025-12-26 19:09:40,377 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 10:50:00
2025-12-26 19:09:40,377 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 11:05:00
2025-12-26 19:09:40,377 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 11:20:00
2025-12-26 19:09:40,378 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 11:35:00
2025-12-26 19:09:40,378 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 10:50:00
2025-12-26 19:09:40,378 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 11:50:00
2025-12-26 19:09:40,378 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 12:05:00
2025-12-26 19:09:40,378 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 12:20:00
2025-12-26 19:09:40,379 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 12:35:00
2025-12-26 19:09:40,379 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 11:50:00
2025-12-26 19:09:40,379 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 12:50:00
2025-12-26 19:09:40,379 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 13:05:00
2025-12-26 19:09:40,379 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 13:20:00
2025-12-26 19:09:40,380 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 13:35:00
2025-12-26 19:09:40,380 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 12:50:00
2025-12-26 19:09:40,380 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 13:50:00
2025-12-26 19:09:40,380 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 14:05:00
2025-12-26 19:09:40,381 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 14:20:00
2025-12-26 19:09:40,381 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 14:35:00
2025-12-26 19:09:40,381 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 13:50:00
2025-12-26 19:09:40,381 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 14:50:00
2025-12-26 19:09:40,382 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 15:05:00
2025-12-26 19:09:40,382 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 15:20:00
2025-12-26 19:09:40,382 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 15:35:00
2025-12-26 19:09:40,382 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 14:50:00
2025-12-26 19:09:40,382 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 15:50:00
2025-12-26 19:09:40,383 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 16:05:00
2025-12-26 19:09:40,383 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 16:20:00
2025-12-26 19:09:40,383 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 16:35:00
2025-12-26 19:09:40,383 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 15:50:00
2025-12-26 19:09:40,384 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 16:50:00
2025-12-26 19:09:40,384 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 17:05:00
2025-12-26 19:09:40,384 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 17:20:00
2025-12-26 19:09:40,384 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 17:35:00
2025-12-26 19:09:40,385 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 16:50:00
2025-12-26 19:09:40,385 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 17:50:00
2025-12-26 19:09:40,385 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 18:05:00
2025-12-26 19:09:40,385 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 18:20:00
2025-12-26 19:09:40,385 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 18:35:00
2025-12-26 19:09:40,386 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 1h candle completed: 2025-12-26 17:50:00
2025-12-26 19:09:40,386 - src.infrastructure.aggregation.data_aggregator - INFO - ✅ 15m candle completed: 2025-12-26 18:50:00
2025-12-26 19:09:40,386 - src.application.services.realtime_service - INFO - ✅ Loaded 500 1m candles
2025-12-26 19:09:40,391 - src.application.services.realtime_service - INFO - 📦 SQLite HIT: 500/500 15m candles
2025-12-26 19:09:40,391 - src.application.services.realtime_service - INFO - ✅ Loaded 499 15m candles
2025-12-26 19:09:40,395 - src.application.services.realtime_service - INFO - 📦 SQLite HIT: 500/500 1h candles
2025-12-26 19:09:40,396 - src.application.services.realtime_service - INFO - ✅ Loaded 499 1h candles
2025-12-26 19:09:40,396 - src.application.services.realtime_service - INFO - ✅ Historical data loaded successfully (SOTA Hybrid)
2025-12-26 19:09:40,396 - src.infrastructure.websocket.binance_websocket_client - INFO - 🚀 SOTA: Multi-stream connection: ['1m', '15m', '1h']
2025-12-26 19:09:40,396 - src.infrastructure.websocket.binance_websocket_client - INFO - Connecting to Binance WebSocket: wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m/btcusdt@kline_15m/btcusdt@kline_1h
2025-12-26 19:09:40,405 - src.application.services.data_retention_service - INFO - 🧹 Starting retention cleanup...
2025-12-26 19:09:40,407 - src.application.services.data_retention_service - INFO - 🧹 Cleanup complete: 0 candles removed, DB size: 0.24 MB
INFO:     Application startup complete.
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): [winerror 10048] only one usage of each socket address (protocol/network address/port) is normally permitted
INFO:     Waiting for application shutdown.
2025-12-26 19:09:40,408 - src.api.main - INFO - Shutting down...
2025-12-26 19:09:40,408 - src.application.services.data_retention_service - INFO - 🧹 DataRetentionService stopped
2025-12-26 19:09:40,409 - src.application.services.realtime_service - WARNING - Service not running
2025-12-26 19:09:40,409 - src.api.event_bus - INFO - Worker cancelled
2025-12-26 19:09:40,409 - src.api.event_bus - INFO - Broadcast Worker Stopped
2025-12-26 19:09:40,409 - src.api.main - INFO - ✅ Shutdown complete
INFO:     Application shutdown complete.

(.venv) E:\Sach\DuAn\Hinto_Stock>