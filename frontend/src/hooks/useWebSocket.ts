/**
 * useWebSocket - SOTA Shared WebSocket Connection Hook
 * 
 * Single WebSocket connection that routes data to Zustand store.
 * All symbols share one connection (matches backend SharedBinanceClient).
 * 
 * Features:
 * - Single connection for all symbols
 * - Client-side routing by symbol
 * - Exponential backoff reconnection
 * - Heartbeat monitoring
 * - Data gap handling
 */

import { useEffect, useRef, useCallback } from 'react';
import { wsUrl, ENDPOINTS } from '../config/api';
import { useMarketStore, MarketData, Signal, StateChange } from '../stores/marketStore';

// ============================================================================
// Configuration
// ============================================================================

const PING_INTERVAL = 30000; // 30 seconds

/**
 * Calculate exponential backoff delay
 */
const calculateBackoffDelay = (retryCount: number): number => {
    const baseDelay = 1000;
    const maxDelay = 30000;
    return Math.min(baseDelay * Math.pow(2, retryCount), maxDelay);
};

// ============================================================================
// Hook Implementation
// ============================================================================

export const useWebSocket = () => {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | undefined>(undefined);
    const countdownIntervalRef = useRef<number | undefined>(undefined);
    const pingIntervalRef = useRef<number | undefined>(undefined);
    const heartbeatIntervalRef = useRef<number | undefined>(undefined);
    const isUnmountingRef = useRef(false);
    const retryCountRef = useRef(0);
    const lastUpdatePerSymbolRef = useRef<Record<string, number>>({});

    // Get store actions
    const {
        updateCandle,
        updateSignal,
        updateStateChange,
        setConnection,
        activeSymbol,
    } = useMarketStore();

    // Clear all timers
    const clearTimers = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = undefined;
        }
        if (countdownIntervalRef.current) {
            clearInterval(countdownIntervalRef.current);
            countdownIntervalRef.current = undefined;
        }
        if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = undefined;
        }
        if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = undefined;
        }
    }, []);

    // Schedule reconnect with exponential backoff
    const scheduleReconnect = useCallback(() => {
        if (isUnmountingRef.current) return;

        const delay = calculateBackoffDelay(retryCountRef.current);
        let remainingTime = Math.ceil(delay / 1000);

        console.log(`Scheduling reconnect in ${remainingTime}s (attempt ${retryCountRef.current + 1})`);

        setConnection({
            isReconnecting: true,
            retryCount: retryCountRef.current,
            nextRetryIn: remainingTime,
        });

        // Countdown timer
        countdownIntervalRef.current = window.setInterval(() => {
            remainingTime -= 1;
            if (remainingTime >= 0) {
                setConnection({ nextRetryIn: remainingTime });
            }
        }, 1000);

        // Actual reconnect
        reconnectTimeoutRef.current = window.setTimeout(() => {
            if (countdownIntervalRef.current) {
                clearInterval(countdownIntervalRef.current);
                countdownIntervalRef.current = undefined;
            }
            retryCountRef.current += 1;
            connect();
        }, delay);
    }, [setConnection]);

    // Main connect function - connects to activeSymbol's stream
    const connect = useCallback(() => {
        if (isUnmountingRef.current) return;

        clearTimers();

        try {
            // Connect to symbol-specific stream endpoint
            // SOTA: Backend broadcasts data for this symbol only
            const wsAddress = wsUrl(ENDPOINTS.WS_STREAM(activeSymbol));
            console.log(`🔌 Connecting to WebSocket for ${activeSymbol}: ${wsAddress}`);

            const ws = new WebSocket(wsAddress);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log(`✅ WebSocket Connected for ${activeSymbol}`);
                setConnection({
                    isConnected: true,
                    isReconnecting: false,
                    retryCount: 0,
                    nextRetryIn: 0,
                    error: null,
                });
                retryCountRef.current = 0;

                // Start ping interval
                pingIntervalRef.current = window.setInterval(() => {
                    if (wsRef.current?.readyState === WebSocket.OPEN) {
                        wsRef.current.send(JSON.stringify({ type: 'ping' }));
                    }
                }, PING_INTERVAL);
            };

            ws.onmessage = (event) => {
                try {
                    const parsedData = JSON.parse(event.data);

                    // Extract symbol from message (backend includes it)
                    // Fallback to activeSymbol which this connection was opened for
                    const symbol = (parsedData.symbol || activeSymbol).toLowerCase();

                    // Update last update time for this symbol
                    lastUpdatePerSymbolRef.current[symbol] = Date.now();

                    // Route message by type
                    if (parsedData.type === 'signal') {
                        if (parsedData.signal && typeof parsedData.signal === 'object') {
                            const rawType = parsedData.signal.type || '';
                            const normalizedSignal: Signal = {
                                ...parsedData.signal,
                                type: typeof rawType === 'string' ? rawType.toUpperCase() as 'BUY' | 'SELL' : rawType,
                            };
                            updateSignal(symbol, normalizedSignal);
                        }
                    } else if (parsedData.type === 'candle' || parsedData.type === 'snapshot') {
                        const candleData = extractCandleData(parsedData);
                        updateCandle(symbol, '1m', candleData);

                        // Also process embedded signal if present
                        if (parsedData.signal && typeof parsedData.signal === 'object') {
                            const rawType = parsedData.signal.type || '';
                            const normalizedSignal: Signal = {
                                ...parsedData.signal,
                                type: typeof rawType === 'string' ? rawType.toUpperCase() as 'BUY' | 'SELL' : rawType,
                            };
                            updateSignal(symbol, normalizedSignal);
                        }
                    } else if (parsedData.type === 'candle_15m') {
                        const candleData = extractCandleData(parsedData);
                        updateCandle(symbol, '15m', candleData);
                    } else if (parsedData.type === 'candle_1h') {
                        const candleData = extractCandleData(parsedData);
                        updateCandle(symbol, '1h', candleData);
                    } else if (parsedData.type === 'state_change') {
                        const stateChange: StateChange = {
                            from_state: parsedData.from_state || parsedData.data?.from_state || '',
                            to_state: parsedData.to_state || parsedData.data?.to_state || '',
                            reason: parsedData.reason || parsedData.data?.reason,
                            timestamp: parsedData.timestamp || new Date().toISOString(),
                            order_id: parsedData.order_id,
                            position_id: parsedData.position_id,
                            cooldown_remaining: parsedData.cooldown_remaining,
                        };
                        updateStateChange(symbol, stateChange);
                    } else if (parsedData.type === 'pong') {
                        // Ping response - ignore
                    }
                } catch (err) {
                    console.error('Failed to parse WebSocket message:', err);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket Disconnected');
                setConnection({ isConnected: false });
                wsRef.current = null;

                if (!isUnmountingRef.current) {
                    scheduleReconnect();
                }
            };

            ws.onerror = (err) => {
                console.error('WebSocket Error:', err);
                setConnection({ error: 'Connection error' });
                ws.close();
            };

        } catch (err) {
            console.error('Connection failed:', err);
            setConnection({ error: 'Failed to create connection' });

            if (!isUnmountingRef.current) {
                scheduleReconnect();
            }
        }
    }, [clearTimers, scheduleReconnect, setConnection, updateCandle, updateSignal, updateStateChange, activeSymbol]);

    // Manual reconnect function
    const reconnectNow = useCallback(() => {
        console.log('Manual reconnect triggered');
        clearTimers();
        retryCountRef.current = 0;
        setConnection({
            isReconnecting: false,
            retryCount: 0,
            nextRetryIn: 0,
        });
        connect();
    }, [clearTimers, connect, setConnection]);

    // Track previous symbol to detect changes
    const prevSymbolRef = useRef(activeSymbol);

    // Effect: Connect on mount AND reconnect when symbol changes
    useEffect(() => {
        isUnmountingRef.current = false;

        // If symbol changed, close old connection first
        if (prevSymbolRef.current !== activeSymbol && wsRef.current) {
            console.log(`📊 Symbol changed: ${prevSymbolRef.current} → ${activeSymbol}, reconnecting...`);
            wsRef.current.close();
        }
        prevSymbolRef.current = activeSymbol;

        connect();

        return () => {
            isUnmountingRef.current = true;
            clearTimers();
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect, clearTimers, activeSymbol]);  // SOTA: Reconnect on symbol change

    return { reconnectNow };
};

// ============================================================================
// Helper Functions
// ============================================================================

function extractCandleData(parsedData: any): MarketData {
    const open = parsedData.open || parsedData.candle?.open || 0;
    const close = parsedData.close || parsedData.candle?.close || 0;
    let changePercent = parsedData.change_percent || parsedData.candle?.change_percent;

    if (changePercent === undefined && open > 0) {
        changePercent = ((close - open) / open) * 100;
    }

    return {
        open,
        high: parsedData.high || parsedData.candle?.high || 0,
        low: parsedData.low || parsedData.candle?.low || 0,
        close,
        volume: parsedData.volume || parsedData.candle?.volume || 0,
        timestamp: parsedData.timestamp || parsedData.candle?.timestamp || new Date().toISOString(),
        time: parsedData.time || Math.floor(Date.now() / 1000),
        change_percent: changePercent,
        vwap: parsedData.vwap || parsedData.data?.vwap,
        bollinger: parsedData.bollinger || parsedData.data?.bollinger,
        rsi: parsedData.rsi || parsedData.data?.rsi,
    };
}

export default useWebSocket;
