import React, { useState, useEffect, useCallback } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { THEME, formatPrice } from '../styles/theme';

// Position interface aligned with backend PaperPosition
interface Position {
    id: string;
    symbol: string;
    side: 'LONG' | 'SHORT';
    status: 'PENDING' | 'OPEN' | 'CLOSED' | 'CANCELLED';
    entry_price: number;
    size: number;  // Renamed from quantity
    leverage: number;
    current_pnl: number;
    current_pnl_pct: number;
    stop_loss: number;
    take_profits: number[];  // Array of TP1, TP2, TP3
    entry_time: string;  // ISO timestamp
    // Legacy fields for backward compatibility
    quantity?: number;
    margin?: number;
    take_profit?: number;
    open_time?: string;
    unrealized_pnl?: number;
}

// Pending order interface
interface PendingOrder {
    id: string;
    signal_id: string;
    symbol: string;
    side: 'LONG' | 'SHORT';
    entry_price: number;
    size: number;
    stop_loss: number;
    take_profits: number[];
    created_at: string;
    expires_at: string;
    ttl_seconds: number;
}

// Portfolio data aligned with backend
interface PortfolioData {
    wallet_balance: number;
    margin_balance: number;
    available_balance: number;
    unrealized_pnl: number;
    total_equity: number;
    open_positions: Position[];
    pending_orders: PendingOrder[];
    // Legacy fields
    balance?: number;
    equity?: number;
    realized_pnl?: number;
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
        // Use size (new) with fallback to quantity (legacy)
        const positionSize = position.size || position.quantity || 0;
        // Use current_pnl from backend if available, otherwise calculate
        if (position.current_pnl !== undefined) return position.current_pnl;
        if (position.side === 'LONG') {
            return (currentPrice - position.entry_price) * positionSize;
        }
        return (position.entry_price - currentPrice) * positionSize;
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
                            // Use current_pnl_pct if available, else calculate from margin
                            const positionMargin = position.margin || (position.entry_price * (position.size || position.quantity || 0));
                            const pnlPercent = position.current_pnl_pct ?? (positionMargin > 0 ? (pnl / positionMargin) * 100 : 0);

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
                                            <div style={{ fontFamily: 'monospace', color: THEME.text.primary }}>{(position.size || position.quantity || 0).toFixed(4)}</div>
                                        </div>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>P&L</span>
                                            <div style={{ fontFamily: 'monospace', fontWeight: 700, color: pnl >= 0 ? THEME.status.buy : THEME.status.sell }}>
                                                {pnl >= 0 ? '+' : ''}{formatPrice(pnl)} ({pnlPercent.toFixed(1)}%)
                                            </div>
                                        </div>
                                    </div>

                                    {/* Entry Time */}
                                    {(position.entry_time || position.open_time) && (
                                        <div style={{ fontSize: '11px', color: THEME.text.tertiary, marginTop: '4px' }}>
                                            📅 Opened: {new Date(position.entry_time || position.open_time || '').toLocaleString('vi-VN')}
                                        </div>
                                    )}

                                    {/* SL/TP Levels */}
                                    <div style={{
                                        display: 'flex',
                                        flexWrap: 'wrap',
                                        gap: '12px',
                                        fontSize: '12px',
                                        marginTop: '8px',
                                        paddingTop: '8px',
                                        borderTop: `1px solid ${THEME.border.primary}`
                                    }}>
                                        <div>
                                            <span style={{ color: THEME.text.tertiary }}>SL</span>
                                            <span style={{ fontFamily: 'monospace', marginLeft: '4px', color: THEME.status.sell }}>${formatPrice(position.stop_loss)}</span>
                                        </div>
                                        {/* TP Levels - use take_profits array or fallback to single take_profit */}
                                        {position.take_profits && position.take_profits.length > 0 ? (
                                            position.take_profits.map((tp, idx) => (
                                                <div key={idx}>
                                                    <span style={{ color: THEME.text.tertiary }}>TP{idx + 1}</span>
                                                    <span style={{ fontFamily: 'monospace', marginLeft: '4px', color: THEME.status.buy }}>${formatPrice(tp)}</span>
                                                </div>
                                            ))
                                        ) : (
                                            <div>
                                                <span style={{ color: THEME.text.tertiary }}>TP</span>
                                                <span style={{ fontFamily: 'monospace', marginLeft: '4px', color: THEME.status.buy }}>${formatPrice(position.take_profit || 0)}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Pending Orders Section */}
            {(portfolio?.pending_orders?.length || 0) > 0 && (
                <div style={{ marginTop: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>
                            ⏳ Lệnh Chờ Khớp
                        </h3>
                        <span style={{ fontSize: '12px', color: THEME.accent.yellow }}>
                            {portfolio?.pending_orders?.length || 0} lệnh
                        </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {portfolio?.pending_orders?.map((order) => (
                            <div key={order.id} style={{
                                ...cardStyle,
                                border: `1px solid ${THEME.accent.yellow}40`,
                                backgroundColor: 'rgba(240, 185, 11, 0.05)'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{
                                            padding: '2px 8px',
                                            borderRadius: '4px',
                                            fontSize: '12px',
                                            fontWeight: 700,
                                            backgroundColor: order.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                            color: order.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                        }}>
                                            {order.side === 'LONG' ? 'MUA' : 'BÁN'}
                                        </span>
                                        <span style={{ fontWeight: 600, color: THEME.text.primary }}>{order.symbol}</span>
                                        <span style={{
                                            fontSize: '10px',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            backgroundColor: THEME.accent.yellow,
                                            color: '#000',
                                            fontWeight: 600,
                                        }}>
                                            PENDING
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => {/* TODO: Cancel order API */ }}
                                        style={{
                                            fontSize: '11px',
                                            padding: '3px 8px',
                                            borderRadius: '4px',
                                            border: 'none',
                                            cursor: 'pointer',
                                            backgroundColor: THEME.bg.vessel,
                                            color: THEME.text.tertiary
                                        }}
                                    >
                                        Hủy
                                    </button>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '12px' }}>
                                    <div>
                                        <span style={{ color: THEME.text.tertiary }}>Entry</span>
                                        <div style={{ fontFamily: 'monospace', color: THEME.accent.yellow }}>${formatPrice(order.entry_price)}</div>
                                    </div>
                                    <div>
                                        <span style={{ color: THEME.text.tertiary }}>Size</span>
                                        <div style={{ fontFamily: 'monospace', color: THEME.text.primary }}>{order.size.toFixed(4)}</div>
                                    </div>
                                    <div>
                                        <span style={{ color: THEME.text.tertiary }}>TTL</span>
                                        <div style={{ fontFamily: 'monospace', color: THEME.accent.yellow }}>
                                            {Math.floor((order.ttl_seconds || 0) / 60)}m {(order.ttl_seconds || 0) % 60}s
                                        </div>
                                    </div>
                                </div>
                                {/* SL/TP for pending order */}
                                <div style={{ display: 'flex', gap: '16px', fontSize: '11px', marginTop: '6px', color: THEME.text.tertiary }}>
                                    <span>SL: <span style={{ color: THEME.status.sell }}>${formatPrice(order.stop_loss)}</span></span>
                                    {order.take_profits && order.take_profits.length > 0 && (
                                        <span>TP1: <span style={{ color: THEME.status.buy }}>${formatPrice(order.take_profits[0])}</span></span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Portfolio;

