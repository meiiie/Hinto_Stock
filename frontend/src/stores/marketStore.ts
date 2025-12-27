/**
 * SOTA Multi-Symbol Market Store
 * 
 * Zustand store for managing real-time market data across multiple symbols.
 * Following Binance patterns for high-frequency trading terminals (Dec 2025).
 * 
 * Features:
 * - Per-symbol data isolation (no cross-contamination)
 * - Instant symbol switching (cached data)
 * - Multi-timeframe support (1m, 15m, 1h)
 * - Signal management per symbol
 * - Connection state tracking
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

// ============================================================================
// Types
// ============================================================================

export interface MarketData {
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    timestamp: string;
    time?: number;
    change_percent?: number;
    rsi?: number;
    vwap?: number;
    bollinger?: {
        upper_band: number;
        lower_band: number;
        middle_band: number;
    };
}

export interface Signal {
    id?: string;
    type: 'BUY' | 'SELL';
    symbol?: string; // SOTA FIX: Signal carries its symbol
    price: number;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    confidence: number;
    risk_reward_ratio: number;
    timestamp: string;
    reason?: string;
    status?: 'generated' | 'pending' | 'executed' | 'expired' | 'rejected';
}

export interface StateChange {
    from_state: string;
    to_state: string;
    reason?: string;
    timestamp: string;
    order_id?: string | null;
    position_id?: string | null;
    cooldown_remaining?: number;
}

export interface SymbolData {
    data1m: MarketData | null;
    data15m: MarketData | null;
    data1h: MarketData | null;
    signal: Signal | null;
    stateChange: StateChange | null;
    lastUpdate: number;
    historicalLoaded: boolean;
}

export interface ConnectionState {
    isConnected: boolean;
    isReconnecting: boolean;
    retryCount: number;
    nextRetryIn: number;
    error: string | null;
}

// ============================================================================
// Store Interface
// ============================================================================

interface MarketStore {
    // Active symbol
    activeSymbol: string;

    // Per-symbol data storage
    symbolData: Record<string, SymbolData>;

    // Connection state (shared across all symbols)
    connection: ConnectionState;

    // Available symbols (from backend)
    availableSymbols: string[];

    // Actions
    setActiveSymbol: (symbol: string) => void;
    updateCandle: (symbol: string, timeframe: '1m' | '15m' | '1h', data: MarketData) => void;
    updateSignal: (symbol: string, signal: Signal) => void;
    updateStateChange: (symbol: string, stateChange: StateChange) => void;
    setHistoricalLoaded: (symbol: string, loaded: boolean) => void;
    setConnection: (state: Partial<ConnectionState>) => void;
    setAvailableSymbols: (symbols: string[]) => void;
    clearSymbolData: (symbol: string) => void;

    // Selectors (computed)
    getActiveData: () => SymbolData | null;
    getDataForSymbol: (symbol: string) => SymbolData | null;
}

// ============================================================================
// Initial State
// ============================================================================

const DEFAULT_SYMBOL = 'btcusdt';

const createEmptySymbolData = (): SymbolData => ({
    data1m: null,
    data15m: null,
    data1h: null,
    signal: null,
    stateChange: null,
    lastUpdate: 0,
    historicalLoaded: false,
});

const initialConnectionState: ConnectionState = {
    isConnected: false,
    isReconnecting: false,
    retryCount: 0,
    nextRetryIn: 0,
    error: null,
};

// ============================================================================
// Store Implementation
// ============================================================================

export const useMarketStore = create<MarketStore>()(
    subscribeWithSelector((set, get) => ({
        // Initial state
        activeSymbol: DEFAULT_SYMBOL,
        symbolData: {
            [DEFAULT_SYMBOL]: createEmptySymbolData(),
        },
        connection: initialConnectionState,
        availableSymbols: ['btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'taousdt', 'fetusdt', 'ondousdt'],

        // Set active symbol (for UI)
        setActiveSymbol: (symbol: string) => {
            const normalizedSymbol = symbol.toLowerCase();
            set((state) => {
                // Ensure symbol data slot exists
                if (!state.symbolData[normalizedSymbol]) {
                    return {
                        activeSymbol: normalizedSymbol,
                        symbolData: {
                            ...state.symbolData,
                            [normalizedSymbol]: createEmptySymbolData(),
                        },
                    };
                }
                return { activeSymbol: normalizedSymbol };
            });

            console.log(`📊 Active symbol changed to: ${normalizedSymbol}`);
        },

        // Update candle data for a specific symbol and timeframe
        updateCandle: (symbol: string, timeframe: '1m' | '15m' | '1h', data: MarketData) => {
            const normalizedSymbol = symbol.toLowerCase();

            set((state) => {
                const existingData = state.symbolData[normalizedSymbol] || createEmptySymbolData();

                const timeframeKey = timeframe === '1m' ? 'data1m'
                    : timeframe === '15m' ? 'data15m'
                        : 'data1h';

                return {
                    symbolData: {
                        ...state.symbolData,
                        [normalizedSymbol]: {
                            ...existingData,
                            [timeframeKey]: data,
                            lastUpdate: Date.now(),
                        },
                    },
                };
            });
        },

        // Update signal for a specific symbol
        updateSignal: (symbol: string, signal: Signal) => {
            const normalizedSymbol = symbol.toLowerCase();

            set((state) => {
                const existingData = state.symbolData[normalizedSymbol] || createEmptySymbolData();

                return {
                    symbolData: {
                        ...state.symbolData,
                        [normalizedSymbol]: {
                            ...existingData,
                            signal,
                            lastUpdate: Date.now(),
                        },
                    },
                };
            });

            console.log(`🎯 Signal updated for ${normalizedSymbol}:`, signal.type);
        },

        // Update state change for a specific symbol
        updateStateChange: (symbol: string, stateChange: StateChange) => {
            const normalizedSymbol = symbol.toLowerCase();

            set((state) => {
                const existingData = state.symbolData[normalizedSymbol] || createEmptySymbolData();

                return {
                    symbolData: {
                        ...state.symbolData,
                        [normalizedSymbol]: {
                            ...existingData,
                            stateChange,
                        },
                    },
                };
            });
        },

        // Mark historical data as loaded for a symbol
        setHistoricalLoaded: (symbol: string, loaded: boolean) => {
            const normalizedSymbol = symbol.toLowerCase();

            set((state) => {
                const existingData = state.symbolData[normalizedSymbol] || createEmptySymbolData();

                return {
                    symbolData: {
                        ...state.symbolData,
                        [normalizedSymbol]: {
                            ...existingData,
                            historicalLoaded: loaded,
                        },
                    },
                };
            });
        },

        // Update connection state
        setConnection: (connectionUpdate: Partial<ConnectionState>) => {
            set((state) => ({
                connection: {
                    ...state.connection,
                    ...connectionUpdate,
                },
            }));
        },

        // Set available symbols from backend
        setAvailableSymbols: (symbols: string[]) => {
            set({ availableSymbols: symbols.map(s => s.toLowerCase()) });
        },

        // Clear data for a specific symbol
        clearSymbolData: (symbol: string) => {
            const normalizedSymbol = symbol.toLowerCase();

            set((state) => ({
                symbolData: {
                    ...state.symbolData,
                    [normalizedSymbol]: createEmptySymbolData(),
                },
            }));
        },

        // Get data for the currently active symbol
        getActiveData: () => {
            const state = get();
            return state.symbolData[state.activeSymbol] || null;
        },

        // Get data for a specific symbol
        getDataForSymbol: (symbol: string) => {
            const state = get();
            return state.symbolData[symbol.toLowerCase()] || null;
        },
    }))
);

// ============================================================================
// Selector Hooks (Performance Optimized)
// ============================================================================

/**
 * Hook to get active symbol data with automatic re-render on change
 */
export const useActiveSymbolData = () => {
    return useMarketStore((state) => state.symbolData[state.activeSymbol] || null);
};

/**
 * Hook to get just the active symbol name
 */
export const useActiveSymbol = () => {
    return useMarketStore((state) => state.activeSymbol);
};

/**
 * Hook to get connection state
 */
export const useConnectionState = () => {
    return useMarketStore((state) => state.connection);
};

/**
 * Hook to get 1m data for active symbol
 */
export const useActiveData1m = () => {
    return useMarketStore((state) => {
        const symbolData = state.symbolData[state.activeSymbol];
        return symbolData?.data1m || null;
    });
};

/**
 * Hook to get 15m data for active symbol
 */
export const useActiveData15m = () => {
    return useMarketStore((state) => {
        const symbolData = state.symbolData[state.activeSymbol];
        return symbolData?.data15m || null;
    });
};

/**
 * Hook to get 1h data for active symbol
 */
export const useActiveData1h = () => {
    return useMarketStore((state) => {
        const symbolData = state.symbolData[state.activeSymbol];
        return symbolData?.data1h || null;
    });
};

/**
 * Hook to get signal for active symbol
 */
export const useActiveSignal = () => {
    return useMarketStore((state) => {
        const symbolData = state.symbolData[state.activeSymbol];
        return symbolData?.signal || null;
    });
};

/**
 * Hook to get state change for active symbol
 */
export const useActiveStateChange = () => {
    return useMarketStore((state) => {
        const symbolData = state.symbolData[state.activeSymbol];
        return symbolData?.stateChange || null;
    });
};

export default useMarketStore;
