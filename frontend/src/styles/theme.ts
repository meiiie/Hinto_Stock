/**
 * Binance-inspired Theme Constants
 * Shared across all components for consistent styling
 */

export const THEME = {
    // Background colors
    bg: {
        primary: '#0B0E11',      // Main background
        secondary: '#181A20',    // Card background
        tertiary: '#1E2329',     // Elevated elements
        vessel: '#29313D',       // Input/container background
        input: '#29313D',
    },
    
    // Text colors
    text: {
        primary: '#EAECEF',      // Main text
        secondary: '#929AA5',    // Secondary text
        tertiary: '#707A8A',     // Muted text
        disabled: '#4F5867',     // Disabled text
    },
    
    // Border/Line colors
    border: {
        primary: '#2B2F36',      // Main border
        secondary: '#333B47',    // Grid lines
        input: '#434C5A',        // Input border
    },
    
    // Status colors
    status: {
        buy: '#2EBD85',          // Green - Buy/Profit
        sell: '#F6465D',         // Red - Sell/Loss
        warning: '#F0B90B',      // Yellow - Warning/VWAP
        info: '#2962FF',         // Blue - Info/Bollinger
        purple: '#8B5CF6',       // Purple - StochRSI
    },
    
    // Background with alpha
    alpha: {
        buyBg: 'rgba(46, 189, 133, 0.1)',
        buyBg20: 'rgba(46, 189, 133, 0.2)',
        sellBg: 'rgba(246, 70, 93, 0.1)',
        sellBg20: 'rgba(246, 70, 93, 0.2)',
        warningBg: 'rgba(240, 185, 11, 0.1)',
        infoBg: 'rgba(41, 98, 255, 0.1)',
    },
    
    // Accent colors
    accent: {
        yellow: '#F0B90B',       // Binance yellow
        gold: '#FCD535',         // Button background
    },
};

/**
 * Format price with locale
 */
export const formatPrice = (price: number, decimals = 2): string => {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(price);
};

/**
 * Format date to Vietnam timezone
 */
export const formatVietnamDate = (dateStr: string | null, options?: Intl.DateTimeFormatOptions): string => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const defaultOptions: Intl.DateTimeFormatOptions = {
        timeZone: 'Asia/Ho_Chi_Minh',
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    };
    return date.toLocaleString('vi-VN', { ...defaultOptions, ...options });
};

/**
 * Format time to Vietnam timezone
 */
export const formatVietnamTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('vi-VN', {
        timeZone: 'Asia/Ho_Chi_Minh',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

/**
 * Calculate duration between two dates
 */
export const calculateDuration = (openTime: string, closeTime: string | null): string => {
    if (!closeTime) return '-';
    const open = new Date(openTime).getTime();
    const close = new Date(closeTime).getTime();
    const diffMs = close - open;
    
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
        const days = Math.floor(hours / 24);
        return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
};

export default THEME;
