import { useState, useEffect, useRef, useCallback } from 'react';

interface MarketData {
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    timestamp: string;
    change_percent?: number;
    rsi?: number;
    vwap?: number;
    bollinger?: {
        upper_band: number;
        lower_band: number;
        middle_band: number;
    };
    [key: string]: any;
}

interface Signal {
    type: 'BUY' | 'SELL';
    price: number;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    confidence: number;
    risk_reward_ratio: number;
    timestamp: string;
    reason?: string;
}

interface ReconnectState {
    isReconnecting: boolean;
    retryCount: number;
    nextRetryIn: number;
}

interface UseMarketDataReturn {
    data: MarketData | null;
    signal: Signal | null;
    isConnected: boolean;
    error: string | null;
    reconnectState: ReconnectState;
    reconnectNow: () => void;
}

/**
 * Calculate exponential backoff delay
 * Formula: delay = min(1000 * (2 ** retries), 30000)
 * Start: 1s, Cap: 30s
 */
const calculateBackoffDelay = (retryCount: number): number => {
    const baseDelay = 1000; // 1 second
    const maxDelay = 30000; // 30 seconds cap
    return Math.min(baseDelay * Math.pow(2, retryCount), maxDelay);
};

/**
 * Custom hook for WebSocket market data streaming
 * 
 * **Feature: desktop-trading-dashboard**
 * **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
 */
export const useMarketData = (symbol: string = 'btcusdt'): UseMarketDataReturn => {
    const [data, setData] = useState<MarketData | null>(null);
    const [signal, setSignal] = useState<Signal | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [reconnectState, setReconnectState] = useState<ReconnectState>({
        isReconnecting: false,
        retryCount: 0,
        nextRetryIn: 0,
    });

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | undefined>(undefined);
    const countdownIntervalRef = useRef<number | undefined>(undefined);
    const isUnmountingRef = useRef(false);
    const retryCountRef = useRef(0);
    const lastUpdateTimeRef = useRef<string | null>(null);

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
    }, []);

    // Fetch missing candles after reconnect (Data Gap Handling)
    const fetchMissingCandles = useCallback(async () => {
        if (!lastUpdateTimeRef.current) return;
        
        try {
            console.log('Fetching missing candles since:', lastUpdateTimeRef.current);
            // TODO: Implement full data gap filling
            // For now, just log the intent - can be expanded later
            const response = await fetch(`http://127.0.0.1:8000/market/history?symbol=${symbol}&limit=100`);
            if (response.ok) {
                const historyData = await response.json();
                console.log('Fetched history data:', historyData.length, 'candles');
            }
        } catch (err) {
            console.error('Failed to fetch missing candles:', err);
        }
    }, [symbol]);

    // Schedule reconnect with exponential backoff
    const scheduleReconnect = useCallback(() => {
        if (isUnmountingRef.current) return;

        const delay = calculateBackoffDelay(retryCountRef.current);
        let remainingTime = Math.ceil(delay / 1000);

        console.log(`Scheduling reconnect in ${remainingTime}s (attempt ${retryCountRef.current + 1})`);

        setReconnectState({
            isReconnecting: true,
            retryCount: retryCountRef.current,
            nextRetryIn: remainingTime,
        });

        // Countdown timer
        countdownIntervalRef.current = window.setInterval(() => {
            remainingTime -= 1;
            if (remainingTime >= 0) {
                setReconnectState(prev => ({
                    ...prev,
                    nextRetryIn: remainingTime,
                }));
            }
        }, 1000);

        // Actual reconnect
        reconnectTimeoutRef.current = window.setTimeout(() => {
            clearTimers();
            retryCountRef.current += 1;
            connect();
        }, delay);
    }, [clearTimers]);

    const connect = useCallback(() => {
        if (isUnmountingRef.current) return;

        clearTimers();

        try {
            const wsUrl = `ws://127.0.0.1:8000/ws/stream/${symbol}`;
            console.log(`Connecting to WebSocket: ${wsUrl}`);

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket Connected');
                setIsConnected(true);
                setError(null);
                setReconnectState({
                    isReconnecting: false,
                    retryCount: 0,
                    nextRetryIn: 0,
                });
                retryCountRef.current = 0; // Reset retry count on success

                // Fetch missing candles if this is a reconnect
                if (lastUpdateTimeRef.current) {
                    fetchMissingCandles();
                }
            };

            ws.onmessage = (event) => {
                try {
                    const parsedData = JSON.parse(event.data);
                    
                    if (parsedData.type === 'signal') {
                        setSignal(parsedData.signal);
                    } else if (parsedData.type === 'candle' || parsedData.type === 'snapshot') {
                        const open = parsedData.open || parsedData.candle?.open || 0;
                        const close = parsedData.close || parsedData.candle?.close || 0;
                        let changePercent = parsedData.change_percent || parsedData.candle?.change_percent;
                        
                        if (changePercent === undefined && open > 0) {
                            changePercent = ((close - open) / open) * 100;
                        }
                        
                        const marketData: MarketData = {
                            open: open,
                            high: parsedData.high || parsedData.candle?.high || 0,
                            low: parsedData.low || parsedData.candle?.low || 0,
                            close: close,
                            volume: parsedData.volume || parsedData.candle?.volume || 0,
                            timestamp: parsedData.timestamp || parsedData.candle?.timestamp || new Date().toISOString(),
                            change_percent: changePercent,
                            vwap: parsedData.vwap || parsedData.data?.vwap,
                            bollinger: parsedData.bollinger || parsedData.data?.bollinger,
                            rsi: parsedData.rsi || parsedData.data?.rsi,
                        };
                        setData(marketData);
                        lastUpdateTimeRef.current = marketData.timestamp; // Track last update
                        
                        if (parsedData.signal) {
                            setSignal(parsedData.signal);
                        }
                    } else if (parsedData.type === 'pong') {
                        // Ping response - ignore
                    } else {
                        setData(parsedData);
                    }
                } catch (err) {
                    console.error('Failed to parse WebSocket message:', err);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket Disconnected');
                setIsConnected(false);
                wsRef.current = null;

                // Auto-reconnect with exponential backoff
                if (!isUnmountingRef.current) {
                    scheduleReconnect();
                }
            };

            ws.onerror = (err) => {
                console.error('WebSocket Error:', err);
                setError('Connection error');
                ws.close();
            };

        } catch (err) {
            console.error('Connection failed:', err);
            setError('Failed to create connection');

            if (!isUnmountingRef.current) {
                scheduleReconnect();
            }
        }
    }, [symbol, clearTimers, scheduleReconnect, fetchMissingCandles]);

    // Manual reconnect function (Reconnect Now button)
    const reconnectNow = useCallback(() => {
        console.log('Manual reconnect triggered');
        clearTimers();
        retryCountRef.current = 0; // Reset retry count
        setReconnectState({
            isReconnecting: false,
            retryCount: 0,
            nextRetryIn: 0,
        });
        connect();
    }, [clearTimers, connect]);

    // Send ping to keep connection alive
    useEffect(() => {
        const pingInterval = setInterval(() => {
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Ping every 30 seconds

        return () => clearInterval(pingInterval);
    }, []);

    useEffect(() => {
        isUnmountingRef.current = false;
        connect();

        return () => {
            isUnmountingRef.current = true;
            clearTimers();
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect, clearTimers]);

    return { data, signal, isConnected, error, reconnectState, reconnectNow };
};
