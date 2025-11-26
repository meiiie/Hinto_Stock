import React, { useState, useEffect, useCallback } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { THEME, formatPrice } from '../styles/theme';

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
 * Portfolio Component - Binance Style with Inline Styles
 * Fixed for Tailwind v4 compatibility
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

    const handleCloseAll = async () => {
        if (!portfolio?.open_positions.length) return;
        if (!confirm(`Đóng tất cả ${portfolio.open_positions.length} vị thế? Hành động này không thể hoàn tác.`)) {
            return;
        }
        try {
            for (const position of portfolio.open_positions) {
                await fetch(`http://127.0.0.1:8000/trades/close/${position.id}`, { method: 'POST' });
            }
            fetchPortfolio();
        } catch (err) {
            console.error('Error closing all positions:', err);
        }
    };

    // Styles
    const containerStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.secondary,
        border: `1px solid ${THEME.border.primary}`,
        borderRadius: '8px',
        padding: '16px',
    };

    const headerStyle: React.CSSProperties = {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingBottom: '12px',
        borderBottom: `1px solid ${THEME.border.primary}`,
        marginBottom: '16px',
    };

    const gridStyle: React.CSSProperties = {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '16px',
    };

    const cardStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.vessel,
        borderRadius: '4px',
        padding: '12px',
    };

    const labelStyle: React.CSSProperties = {
        fontSize: '12px',
        color: THEME.text.tertiary,
        marginBottom: '4px',
    };

    const valueStyle: React.CSSProperties = {
        fontSize: '20px',
        fontWeight: 700,
        fontFamily: 'monospace',
        color: THEME.text.primary,
    };

    if (isLoading) {
        return (
            <div style={containerStyle}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ height: '16px', backgroundColor: THEME.bg.vessel, borderRadius: '4px', width: '33%' }}></div>
                    <div style={{ height: '32px', backgroundColor: THEME.bg.vessel, borderRadius: '4px' }}></div>
                    <div style={{ height: '32px', backgroundColor: THEME.bg.vessel, borderRadius: '4px' }}></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ ...containerStyle, borderColor: THEME.status.sell }}>
                <p style={{ fontSize: '14px', color: THEME.status.sell, margin: 0 }}>{error}</p>
            </div>
        );
    }

    const totalUnrealizedPnL = portfolio?.open_positions.reduce((sum, pos) => sum + calculatePositionPnL(pos), 0) || 0;

    return (
        <div style={containerStyle}>
            {/* Header */}
            <div style={headerStyle}>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: THEME.text.primary, margin: 0 }}>Portfolio</h2>
                <span style={{ 
                    fontSize: '12px', 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    backgroundColor: THEME.alpha.warningBg, 
                    color: THEME.accent.yellow 
                }}>
                    Paper Trading
                </span>
            </div>

            {/* Balance Summary */}
            <div style={gridStyle}>
                <div style={cardStyle}>
                    <div style={labelStyle}>Số dư</div>
                    <div style={valueStyle}>${formatPrice(portfolio?.balance || 0)}</div>
                </div>
                <div style={cardStyle}>
                    <div style={labelStyle}>Vốn chủ sở hữu</div>
                    <div style={valueStyle}>${formatPrice((portfolio?.balance || 0) + totalUnrealizedPnL)}</div>
                </div>
            </div>

            {/* PnL Summary */}
            <div style={gridStyle}>
                <div style={cardStyle}>
                    <div style={labelStyle}>Lãi/Lỗ chưa thực hiện</div>
                    <div style={{ 
                        ...valueStyle, 
                        fontSize: '18px',
                        color: totalUnrealizedPnL >= 0 ? THEME.status.buy : THEME.status.sell 
                    }}>
                        {totalUnrealizedPnL >= 0 ? '+' : ''}{formatPrice(totalUnrealizedPnL)}
                    </div>
                </div>
                <div style={cardStyle}>
                    <div style={labelStyle}>Lãi/Lỗ đã thực hiện</div>
                    <div style={{ 
                        ...valueStyle, 
                        fontSize: '18px',
                        color: (portfolio?.realized_pnl || 0) >= 0 ? THEME.status.buy : THEME.status.sell 
                    }}>
                        {(portfolio?.realized_pnl || 0) >= 0 ? '+' : ''}{formatPrice(portfolio?.realized_pnl || 0)}
                    </div>
                </div>
            </div>

            {/* Open Positions */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>Vị thế đang mở</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '12px', color: THEME.text.tertiary }}>
                            {portfolio?.open_positions.length || 0} vị thế
                        </span>
                        {(portfolio?.open_positions.length || 0) > 0 && (
                            <button
                                onClick={handleCloseAll}
                                style={{ 
                                    fontSize: '12px',
                                    padding: '4px 12px',
                                    borderRadius: '4px',
                                    fontWeight: 700,
                                    border: 'none',
                                    cursor: 'pointer',
                                    backgroundColor: THEME.status.sell, 
                                    color: '#fff',
                                    boxShadow: '0 2px 8px rgba(246, 70, 93, 0.4)'
                                }}
                            >
                                🚨 ĐÓNG TẤT CẢ
                            </button>
                        )}
                    </div>
                </div>

                {portfolio?.open_positions.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '24px', fontSize: '14px', color: THEME.text.tertiary }}>
                        Không có vị thế nào
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '256px', overflowY: 'auto' }}>
                        {portfolio?.open_positions.map((position) => {
                            const pnl = calculatePositionPnL(position);
                            const pnlPercent = position.margin > 0 ? (pnl / position.margin) * 100 : 0;
                            
                            return (
                                <div key={position.id} style={{ 
                                    ...cardStyle, 
                                    border: `1px solid ${THEME.border.primary}` 
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{
                                                padding: '2px 8px',
                                                borderRadius: '4px',
                                                fontSize: '12px',
                                                fontWeight: 700,
                                                backgroundColor: position.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                                color: position.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                            }}>
                                                {position.side === 'LONG' ? 'MUA' : 'BÁN'}
                                            </span>
                                            <span style={{ fontWeight: 600, color: THEME.text.primary }}>{position.symbol}</span>
                                        </div>
                                        <button 
                                            onClick={() => handleClosePosition(position.id)}
                                            style={{
                                                fontSize: '12px',
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                border: 'none',
                                                cursor: 'pointer',
                                                backgroundColor: THEME.status.sell,
                                                color: '#fff'
                                            }}
                                        >
                                            Đóng
                                        </button>
                                    </div>
                                    
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '12px' }}>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>Entry</span>
                                            <div style={{ fontFamily: 'monospace', color: THEME.text.primary }}>${formatPrice(position.entry_price)}</div>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>Size</span>
                                            <div style={{ fontFamily: 'monospace', color: THEME.text.primary }}>{position.quantity.toFixed(4)}</div>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>P&L</span>
                                            <div style={{ fontFamily: 'monospace', fontWeight: 700, color: pnl >= 0 ? THEME.status.buy : THEME.status.sell }}>
                                                {pnl >= 0 ? '+' : ''}{formatPrice(pnl)} ({pnlPercent.toFixed(1)}%)
                                            </div>
                                        </div>
                                    </div>

                                    <div style={{ 
                                        display: 'grid', 
                                        gridTemplateColumns: '1fr 1fr', 
                                        gap: '8px', 
                                        fontSize: '12px', 
                                        marginTop: '8px', 
                                        paddingTop: '8px', 
                                        borderTop: `1px solid ${THEME.border.primary}` 
                                    }}>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>SL</span>
                                            <span style={{ fontFamily: 'monospace', marginLeft: '8px', color: THEME.status.sell }}>${formatPrice(position.stop_loss)}</span>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>TP</span>
                                            <span style={{ fontFamily: 'monospace', marginLeft: '8px', color: THEME.status.buy }}>${formatPrice(position.take_profit)}</span>
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
