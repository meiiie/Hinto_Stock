/**
 * API Configuration - Centralized endpoint management
 * 
 * SOTA Best Practice: Environment-based configuration
 * All API URLs are managed here to enable easy deployment to different environments.
 * 
 * Usage:
 *   import { API_BASE_URL, WS_BASE_URL, apiUrl } from '@/config/api';
 *   
 *   fetch(apiUrl('/trades/portfolio'))
 *   new WebSocket(wsUrl('/ws/stream/btcusdt'))
 */

// Base URLs from environment variables or defaults
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000';

/**
 * Build full API URL
 * @param path - API path (e.g., '/trades/portfolio')
 * @returns Full URL (e.g., 'http://127.0.0.1:8000/trades/portfolio')
 */
export const apiUrl = (path: string): string => {
    // Ensure path starts with /
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
};

/**
 * Build full WebSocket URL
 * @param path - WS path (e.g., '/ws/stream/btcusdt')
 * @returns Full URL (e.g., 'ws://127.0.0.1:8000/ws/stream/btcusdt')
 */
export const wsUrl = (path: string): string => {
    // Ensure path starts with /
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${WS_BASE_URL}${normalizedPath}`;
};

// Pre-defined endpoint paths for consistency
export const ENDPOINTS = {
    // Market data
    MARKET_HISTORY: (symbol: string, limit: number = 100) =>
        `/market/history?symbol=${symbol}&limit=${limit}`,
    WS_HISTORY: (symbol: string, timeframe: string, limit: number = 1) =>
        `/ws/history/${symbol}?timeframe=${timeframe}&limit=${limit}`,
    WS_STREAM: (symbol: string) => `/ws/stream/${symbol}`,

    // Trading
    PORTFOLIO: '/trades/portfolio',
    TRADE_HISTORY: (page: number = 1, limit: number = 20) =>
        `/trades/history?page=${page}&limit=${limit}`,
    EXECUTE_TRADE: (positionId: string) => `/trades/execute/${positionId}`,
    CLOSE_POSITION: (positionId: string) => `/trades/close/${positionId}`,
    RESET_TRADES: '/trades/reset',
    SIMULATE_TRADE: '/trades/simulate',

    // Performance
    PERFORMANCE: (days: number) => `/trades/performance?days=${days}`,
    EQUITY_CURVE: (days: number, resolution: string = 'trade') =>
        `/trades/equity-curve?days=${days}&resolution=${resolution}`,

    // System
    SYSTEM_STATUS: '/system/status',
    SETTINGS: '/settings',
};

export default {
    API_BASE_URL,
    WS_BASE_URL,
    apiUrl,
    wsUrl,
    ENDPOINTS,
};
