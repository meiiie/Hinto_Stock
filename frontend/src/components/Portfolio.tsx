import React, { useState, useEffect, useCallback } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { THEME, formatPrice, formatVietnamDate } from '../styles/theme';

interface Position {
    id: string;
    symbol: string;
    side: 'LONG' | 'SHORT';
    status: string;
    entry_price: number;
    quantity: number;
    margin: number;
    stop_loss: number;
    take_profit: number;
    open_time: string;
    unrealized_pnl?: number;
}

interface PortfolioData {
    balance: number;
    equity: number;
    unrealized_pnl: number;
    realized_pnl: number;
    open_positions: Position[];
}

/**
 * Portfolio Component - Binance Style
 * Displays virtual balance, equity, unrealized PnL, and open positions
 */
const Portfolio: React.FC = () => {
    const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    const { data: marketData } = useMarketData('btcusdt');
    const currentPrice = marketData?.close || 0;

    const fetchPortfolio = useCallback(async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/trades/portfolio');
            if (!response.ok) throw new Error('Failed to fetch portfolio');
            const data = await response.json();
            setPortfolio(data);
            setError(null);
        } catch (err) {
            setError('Không thể tải portfolio');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        const interval = setInterval(fetchPortfolio, 5000);
        return () => clearInterval(interval);
    }, [fetchPortfolio]);

    const calculatePositionPnL = (position: Position): number => {
        if (currentPrice <= 0) return 0;
        if (position.side === 'LONG') {
            return (currentPrice - position.entry_price) * position.quantity;
        }
        return (position.entry_price - currentPrice) * position.quantity;
    };

    const handleClosePosition = async (positionId: string) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/trades/close/${positionId}`, { method: 'POST' });
            if (response.ok) fetchPortfolio();
        } catch (err) {
            console.error('Error closing position:', err);
        }
    };

    if (isLoading) {
        return (
            <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
                <div className="animate-pulse space-y-3">
                    <div className="h-4 rounded w-1/3" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    <div className="h-8 rounded" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    <div className="h-8 rounded" style={{ backgroundColor: THEME.bg.vessel }}></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.status.sell}` }}>
                <p className="text-sm" style={{ color: THEME.status.sell }}>{error}</p>
            </div>
        );
    }

    const totalUnrealizedPnL = portfolio?.open_positions.reduce((sum, pos) => sum + calculatePositionPnL(pos), 0) || 0;

    return (
        <div className="rounded-lg p-4 space-y-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
            {/* Header */}
            <div className="flex justify-between items-center pb-3" style={{ borderBottom: `1px solid ${THEME.border.primary}` }}>
                <h2 className="text-lg font-bold" style={{ color: THEME.text.primary }}>Portfolio</h2>
                <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: THEME.alpha.warningBg, color: THEME.accent.yellow }}>
                    Paper Trading
                </span>
            </div>

            {/* Balance Summary */}
            <div className="grid grid-cols-2 gap-3">
                <div className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel }}>
                    <div className="text-xs mb-1" style={{ color: THEME.text.tertiary }}>Số dư</div>
                    <div className="text-xl font-bold font-mono" style={{ color: THEME.text.primary }}>
                        ${formatPrice(portfolio?.balance || 0)}
                    </div>
                </div>
                <div className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel }}>
                    <div className="text-xs mb-1" style={{ color: THEME.text.tertiary }}>Vốn chủ sở hữu</div>
                    <div className="text-xl font-bold font-mono" style={{ color: THEME.text.primary }}>
                        ${formatPrice((portfolio?.balance || 0) + totalUnrealizedPnL)}
                    </div>
                </div>
            </div>

            {/* PnL Summary */}
            <div className="grid grid-cols-2 gap-3">
                <div className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel }}>
                    <div className="text-xs mb-1" style={{ color: THEME.text.tertiary }}>Lãi/Lỗ chưa thực hiện</div>
                    <div className="text-lg font-bold font-mono" style={{ color: totalUnrealizedPnL >= 0 ? THEME.status.buy : THEME.status.sell }}>
                        {totalUnrealizedPnL >= 0 ? '+' : ''}{formatPrice(totalUnrealizedPnL)}
                    </div>
                </div>
                <div className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel }}>
                    <div className="text-xs mb-1" style={{ color: THEME.text.tertiary }}>Lãi/Lỗ đã thực hiện</div>
                    <div className="text-lg font-bold font-mono" style={{ color: (portfolio?.realized_pnl || 0) >= 0 ? THEME.status.buy : THEME.status.sell }}>
                        {(portfolio?.realized_pnl || 0) >= 0 ? '+' : ''}{formatPrice(portfolio?.realized_pnl || 0)}
                    </div>
                </div>
            </div>

            {/* Open Positions */}
            <div>
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-sm font-semibold" style={{ color: THEME.text.secondary }}>Vị thế đang mở</h3>
                    <span className="text-xs" style={{ color: THEME.text.tertiary }}>
                        {portfolio?.open_positions.length || 0} vị thế
                    </span>
                </div>

                {portfolio?.open_positions.length === 0 ? (
                    <div className="text-center py-6 text-sm" style={{ color: THEME.text.tertiary }}>
                        Không có vị thế nào
                    </div>
                ) : (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {portfolio?.open_positions.map((position) => {
                            const pnl = calculatePositionPnL(position);
                            const pnlPercent = position.margin > 0 ? (pnl / position.margin) * 100 : 0;
                            
                            return (
                                <div key={position.id} className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel, border: `1px solid ${THEME.border.primary}` }}>
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="px-2 py-0.5 rounded text-xs font-bold" style={{
                                                backgroundColor: position.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                                color: position.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                            }}>
                                                {position.side === 'LONG' ? 'MUA' : 'BÁN'}
                                            </span>
                                            <span className="font-semibold" style={{ color: THEME.text.primary }}>{position.symbol}</span>
                                        </div>
                                        <button onClick={() => handleClosePosition(position.id)}
                                            className="text-xs px-2 py-1 rounded transition-colors hover:opacity-80"
                                            style={{ backgroundColor: THEME.status.sell, color: '#fff' }}>
                                            Đóng
                                        </button>
                                    </div>
                                    
                                    <div className="grid grid-cols-3 gap-2 text-xs">
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>Entry</span>
                                            <div className="font-mono" style={{ color: THEME.text.primary }}>${formatPrice(position.entry_price)}</div>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>Size</span>
                                            <div className="font-mono" style={{ color: THEME.text.primary }}>{position.quantity.toFixed(4)}</div>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>P&L</span>
                                            <div className="font-mono font-bold" style={{ color: pnl >= 0 ? THEME.status.buy : THEME.status.sell }}>
                                                {pnl >= 0 ? '+' : ''}{formatPrice(pnl)} ({pnlPercent.toFixed(1)}%)
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-2 text-xs mt-2 pt-2" style={{ borderTop: `1px solid ${THEME.border.primary}` }}>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>SL</span>
                                            <span className="font-mono ml-2" style={{ color: THEME.status.sell }}>${formatPrice(position.stop_loss)}</span>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>TP</span>
                                            <span className="font-mono ml-2" style={{ color: THEME.status.buy }}>${formatPrice(position.take_profit)}</span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Portfolio;
