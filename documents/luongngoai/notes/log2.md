Traceback (most recent call last):
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 125, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 111, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 391, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 290, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "e:\Sach\DuAn\Hinto_Stock\src\api\routers\system.py", line 155, in debug_signal_check
    state_machine = realtime_service.state_machine
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'RealtimeService' object has no attribute 'state_machine'
INFO:     127.0.0.1:22709 - "GET /system/debug/signal-check HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 403, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\applications.py", line 1134, in __call__
    await super().__call__(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 125, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 111, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 391, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "E:\Sach\DuAn\Hinto_Stock\.venv\Lib\site-packages\fastapi\routing.py", line 290, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "e:\Sach\DuAn\Hinto_Stock\src\api\routers\system.py", line 155, in debug_signal_check
    state_machine = realtime_service.state_machine
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'RealtimeService' object has no attribute 'state_machine'
2025-12-29 01:13:09,816 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1m] Candle: 124.17 - notifying 1 callbacks
2025-12-29 01:13:09,816 - src.application.services.realtime_service - INFO - 🕯️ [1m] Caandle: 124.17 closed=False symbol=solusdt
2025-12-29 01:13:09,818 - src.infrastructure.indicators.talib_calculator - INFO - Indicators calculated: EMA7(95/101), EMA25(77/101), RSI(95/101), VMA(82/101)
2025-12-29 01:13:09,826 - src.application.services.realtime_service - INFO - 📢 Calling _notify_update_callbacks with 0 callbacks
2025-12-29 01:13:09,826 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [15m] Candle: 124.17 - notifying 1 callbacks
2025-12-29 01:13:09,826 - src.application.services.realtime_service - INFO - 🕯️ [15m] CCandle: 124.17 closed=False symbol=solusdt
2025-12-29 01:13:09,826 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1h] Candle: 124.17 - notifying 1 callbacks
2025-12-29 01:13:09,826 - src.application.services.realtime_service - INFO - 🕯️ [1h] Caandle: 124.17 closed=False symbol=solusdt
2025-12-29 01:13:11,046 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1m] Candle: 87705.47 - notifying 1 callbacks
2025-12-29 01:13:11,047 - src.application.services.realtime_service - INFO - 🕯️ [1m] Caandle: 87705.47 closed=False symbol=btcusdt
2025-12-29 01:13:11,052 - src.infrastructure.indicators.talib_calculator - INFO - Indicators calculated: EMA7(95/101), EMA25(77/101), RSI(95/101), VMA(82/101)
2025-12-29 01:13:11,061 - src.application.services.realtime_service - INFO - 📢 Calling _notify_update_callbacks with 0 callbacks
2025-12-29 01:13:11,061 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [15m] Candle: 87705.47 - notifying 1 callbacks
2025-12-29 01:13:11,061 - src.application.services.realtime_service - INFO - 🕯️ [15m] CCandle: 87705.47 closed=False symbol=btcusdt
2025-12-29 01:13:11,062 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1h] Candle: 87705.47 - notifying 1 callbacks
2025-12-29 01:13:11,062 - src.application.services.realtime_service - INFO - 🕯️ [1h] Caandle: 87705.47 closed=False symbol=btcusdt
2025-12-29 01:13:11,064 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1m] Candle: 2943.47 - notifying 1 callbacks
2025-12-29 01:13:11,064 - src.application.services.realtime_service - INFO - 🕯️ [1m] Caandle: 2943.47 closed=False symbol=ethusdt
2025-12-29 01:13:11,066 - src.infrastructure.indicators.talib_calculator - INFO - Indicators calculated: EMA7(95/101), EMA25(77/101), RSI(95/101), VMA(82/101)
2025-12-29 01:13:11,075 - src.application.services.realtime_service - INFO - 📢 Calling _notify_update_callbacks with 0 callbacks
2025-12-29 01:13:11,076 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [15m] Candle: 2943.47 - notifying 1 callbacks
2025-12-29 01:13:11,076 - src.application.services.realtime_service - INFO - 🕯️ [15m] CCandle: 2943.47 closed=False symbol=ethusdt
2025-12-29 01:13:11,076 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1h] Candle: 2943.47 - notifying 1 callbacks
2025-12-29 01:13:11,076 - src.application.services.realtime_service - INFO - 🕯️ [1h] Caandle: 2943.47 closed=False symbol=ethusdt
2025-12-29 01:13:11,123 - src.infrastructure.websocket.binance_websocket_client - INFO - 📊 [1m] Candle: 863.47 - notifying 1 callbacks
2025-12-29 01:13:11,123 - src.application.services.realtime_service - INFO - 🕯️ [1m] Caandle: 863.47 closed=False symbol=bnbusdt
2025-12-29 01:13:11,125 - src.infrastructure.indicators.talib_calculator - INFO - Indicators calculated: EMA7(95/101), EMA25(77/101), RSI(95/101), VMA(82/101)
2025-12-29 01:13:11,133 - src.application.services.realtime_service - INFO - 📢 Calling _notify_update_callbacks with 0 callbacks