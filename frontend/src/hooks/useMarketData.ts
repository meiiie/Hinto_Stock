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

interface UseMarketDataReturn {
    data: MarketData | null;
    signal: Signal | null;
    isConnected: boolean;
    error: string | null;
}

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

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | undefined>(undefined);
    const isUnmountingRef = useRef(false);

    const connect = useCallback(() => {
        if (isUnmountingRef.current) return;

        try {
            // Use the new stream endpoint
            const wsUrl = `ws://127.0.0.1:8000/ws/stream/${symbol}`;
            console.log(`Connecting to WebSocket: ${wsUrl}`);

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket Connected');
                setIsConnected(true);
                setError(null);
            };

            ws.onmessage = (event) => {
                try {
                    const parsedData = JSON.parse(event.data);
                    
                    // Handle different message types
                    if (parsedData.type === 'signal') {
                        // Signal notification
                        setSignal(parsedData.signal);
                    } else if (parsedData.type === 'candle' || parsedData.type === 'snapshot') {
                        // Market data update
                        // Calculate change_percent from open and close if not provided
                        const open = parsedData.open || parsedData.candle?.open || 0;
                        const close = parsedData.close || parsedData.candle?.close || 0;
                        let changePercent = parsedData.change_percent || parsedData.candle?.change_percent;
                        
                        // Calculate if not provided and open > 0
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
                        
                        // Check if signal is included in the data
                        if (parsedData.signal) {
                            setSignal(parsedData.signal);
                        }
                    } else if (parsedData.type === 'pong') {
                        // Ping response - ignore
                    } else {
                        // Legacy format - treat as market data
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

                // Auto-reconnect every 5 seconds if not unmounting
                if (!isUnmountingRef.current) {
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        console.log('Attempting to reconnect...');
                        connect();
                    }, 5000);
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
                reconnectTimeoutRef.current = window.setTimeout(connect, 5000);
            }
        }
    }, [symbol]);

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
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connect]);

    return { data, signal, isConnected, error };
};
