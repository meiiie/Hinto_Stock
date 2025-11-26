import React, { useState, useEffect, useCallback } from 'react';
import { THEME, formatPrice, formatVietnamDate, calculateDuration } from '../styles/theme';

interface Trade {
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
    close_time: string | null;
    realized_pnl: number;
    exit_reason: string | null;
}

interface PaginatedTrades {
    trades: Trade[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
}

/**
 * Trade History Component - Binance Style with Inline Styles
 * Fixed for Tailwind v4 compatibility
 */
const TradeHistory: React.FC = () => {
    const [trades, setTrades] = useState<PaginatedTrades | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const limit = 10;

    const fetchTrades = useCallback(async (page: number) => {
        setIsLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/trades/history?page=${page}&limit=${limit}`);
            if (!response.ok) throw new Error('Failed to fetch trades');
            const data = await response.json();
            setTrades(data);
            setError(null);
        } catch (err) {
            setError('Không thể tải lịch sử giao dịch');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTrades(currentPage);
    }, [currentPage, fetchTrades]);

    const getExitReasonBadge = (reason: string | null) => {
        if (!reason) return null;
        const config: Record<string, { bg: string; color: string; label: string }> = {
            'TAKE_PROFIT': { bg: THEME.alpha.buyBg, color: THEME.status.buy, label: 'Chốt lời' },
            'STOP_LOSS': { bg: THEME.alpha.sellBg, color: THEME.status.sell, label: 'Cắt lỗ' },
            'MANUAL_CLOSE': { bg: THEME.alpha.infoBg, color: THEME.status.info, label: 'Đóng tay' },
            'SIGNAL_REVERSAL': { bg: THEME.alpha.warningBg, color: THEME.accent.yellow, label: 'Đảo chiều' },
        };
        const c = config[reason] || { bg: THEME.bg.vessel, color: THEME.text.tertiary, label: reason };
        return (
            <span style={{ 
                display: 'inline-block',
                padding: '3px 8px', 
                borderRadius: '4px', 
                fontSize: '10px', 
                fontWeight: 600,
                backgroundColor: c.bg, 
                color: c.color,
                whiteSpace: 'nowrap',
            }}>
                {c.label}
            </span>
        );
    };

    // Container style
    const containerStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.secondary,
        border: `1px solid ${THEME.border.primary}`,
        borderRadius: '8px',
        padding: '16px',
    };

    if (isLoading && !trades) {
        return (
            <div style={containerStyle}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ height: '16px', backgroundColor: THEME.bg.vessel, borderRadius: '4px', width: '33%' }}></div>
                    {[...Array(5)].map((_, i) => (
                        <div key={i} style={{ height: '48px', backgroundColor: THEME.bg.vessel, borderRadius: '4px' }}></div>
                    ))}
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

    return (
        <div style={containerStyle}>
            {/* Header */}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                paddingBottom: '12px', 
                borderBottom: `1px solid ${THEME.border.primary}`, 
                marginBottom: '16px' 
            }}>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: THEME.text.primary, margin: 0 }}>Lịch sử giao dịch</h2>
                <span style={{ fontSize: '12px', color: THEME.text.tertiary }}>
                    {trades?.total || 0} giao dịch
                </span>
            </div>

            {/* Table */}
            {trades?.trades.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px', color: THEME.text.tertiary }}>
                    Chưa có giao dịch nào
                </div>
            ) : (
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', tableLayout: 'fixed', minWidth: '700px' }}>
                        <thead>
                            <tr style={{ borderBottom: `2px solid ${THEME.border.primary}`, backgroundColor: THEME.bg.vessel }}>
                                <th style={{ width: '110px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'left' }}>Thời gian</th>
                                <th style={{ width: '80px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'left' }}>Cặp</th>
                                <th style={{ width: '60px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'center' }}>Loại</th>
                                <th style={{ width: '100px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'right' }}>Entry</th>
                                <th style={{ width: '100px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'right' }}>Exit</th>
                                <th style={{ width: '90px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'right' }}>P&L</th>
                                <th style={{ width: '70px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'center' }}>Thời gian</th>
                                <th style={{ width: '90px', padding: '10px 8px', fontSize: '11px', color: THEME.text.tertiary, fontWeight: 600, textAlign: 'center' }}>Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trades?.trades.map((trade, index) => (
                                <tr 
                                    key={trade.id} 
                                    style={{ 
                                        borderBottom: `1px solid ${THEME.border.secondary}`,
                                        backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(30,35,41,0.3)',
                                    }}
                                >
                                    <td style={{ padding: '10px 8px', fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: THEME.text.secondary }}>
                                        {formatVietnamDate(trade.close_time || trade.open_time)}
                                    </td>
                                    <td style={{ padding: '10px 8px', fontWeight: 600, color: THEME.text.primary, fontSize: '12px' }}>
                                        {trade.symbol}
                                    </td>
                                    <td style={{ padding: '10px 8px', textAlign: 'center' }}>
                                        <span style={{
                                            display: 'inline-block',
                                            padding: '3px 8px',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            fontWeight: 700,
                                            backgroundColor: trade.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                            color: trade.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                        }}>
                                            {trade.side === 'LONG' ? 'MUA' : 'BÁN'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: THEME.text.primary }}>
                                        ${formatPrice(trade.entry_price)}
                                    </td>
                                    <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: THEME.text.secondary }}>
                                        {trade.exit_reason === 'TAKE_PROFIT' ? `$${formatPrice(trade.take_profit)}` :
                                         trade.exit_reason === 'STOP_LOSS' ? `$${formatPrice(trade.stop_loss)}` : '-'}
                                    </td>
                                    <td style={{ 
                                        padding: '10px 8px',
                                        textAlign: 'right', 
                                        fontFamily: "'JetBrains Mono', monospace", 
                                        fontSize: '12px',
                                        fontWeight: 700,
                                        color: trade.realized_pnl >= 0 ? THEME.status.buy : THEME.status.sell 
                                    }}>
                                        {trade.realized_pnl >= 0 ? '+' : ''}{formatPrice(trade.realized_pnl)}
                                    </td>
                                    <td style={{ padding: '10px 8px', textAlign: 'center', fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: THEME.text.tertiary }}>
                                        {calculateDuration(trade.open_time, trade.close_time)}
                                    </td>
                                    <td style={{ padding: '10px 8px', textAlign: 'center' }}>
                                        {getExitReasonBadge(trade.exit_reason)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Pagination */}
            {trades && trades.total_pages > 1 && (
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    marginTop: '16px', 
                    paddingTop: '12px', 
                    borderTop: `1px solid ${THEME.border.primary}` 
                }}>
                    <span style={{ fontSize: '12px', color: THEME.text.tertiary }}>
                        Trang {trades.page} / {trades.total_pages}
                    </span>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            style={{ 
                                padding: '6px 16px',
                                fontSize: '12px',
                                borderRadius: '4px',
                                border: 'none',
                                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                backgroundColor: THEME.bg.vessel,
                                color: THEME.text.secondary,
                                opacity: currentPage === 1 ? 0.5 : 1,
                            }}
                        >
                            Trước
                        </button>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(trades.total_pages, p + 1))}
                            disabled={currentPage === trades.total_pages}
                            style={{ 
                                padding: '6px 16px',
                                fontSize: '12px',
                                borderRadius: '4px',
                                border: 'none',
                                cursor: currentPage === trades.total_pages ? 'not-allowed' : 'pointer',
                                backgroundColor: THEME.bg.vessel,
                                color: THEME.text.secondary,
                                opacity: currentPage === trades.total_pages ? 0.5 : 1,
                            }}
                        >
                            Sau
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TradeHistory;
