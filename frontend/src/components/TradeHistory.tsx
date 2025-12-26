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
 * Trade History Component - Binance SOTA Professional Style
 * 
 * SOTA Features:
 * - Uppercase symbols
 * - P&L with both $ and %
 * - Calculated exit prices
 * - Professional badges with icons
 * - Improved pagination
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

    // SOTA: Calculate exit price from entry and P&L
    const calculateExitPrice = (trade: Trade): number | null => {
        if (!trade.quantity || trade.quantity === 0) return null;
        // For LONG: exit = entry + (pnl / qty)
        // For SHORT: exit = entry - (pnl / qty)
        const pnlPerUnit = trade.realized_pnl / trade.quantity;
        return trade.side === 'LONG'
            ? trade.entry_price + pnlPerUnit
            : trade.entry_price - pnlPerUnit;
    };

    // SOTA: Calculate P&L percentage
    const calculatePnlPercent = (trade: Trade): number => {
        if (!trade.margin || trade.margin === 0) return 0;
        return (trade.realized_pnl / trade.margin) * 100;
    };

    // SOTA: Professional exit reason badges with icons
    const getExitReasonBadge = (reason: string | null) => {
        if (!reason) return <span style={{ color: THEME.text.tertiary }}>-</span>;

        const config: Record<string, { bg: string; color: string; label: string; icon: string }> = {
            'TAKE_PROFIT': { bg: THEME.alpha.buyBg, color: THEME.status.buy, label: 'Chốt lời', icon: '🎯' },
            'STOP_LOSS': { bg: THEME.alpha.sellBg, color: THEME.status.sell, label: 'Cắt lỗ', icon: '🛡️' },
            'MANUAL_CLOSE': { bg: THEME.alpha.infoBg, color: THEME.status.info, label: 'Đóng tay', icon: '✋' },
            'SIGNAL_REVERSAL': { bg: THEME.alpha.warningBg, color: THEME.accent.yellow, label: 'Đảo chiều', icon: '🔄' },
            'MERGED': { bg: 'rgba(128,128,128,0.15)', color: THEME.text.secondary, label: 'Merged', icon: '🔗' },
        };

        const c = config[reason] || { bg: THEME.bg.vessel, color: THEME.text.tertiary, label: reason, icon: '📝' };

        return (
            <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: 600,
                backgroundColor: c.bg,
                color: c.color,
                whiteSpace: 'nowrap',
            }}>
                <span>{c.icon}</span>
                <span>{c.label}</span>
            </span>
        );
    };

    // Container style
    const containerStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.secondary,
        border: `1px solid ${THEME.border.primary}`,
        borderRadius: '8px',
        padding: '20px',
    };

    // Table header style
    const thStyle = (align: 'left' | 'center' | 'right' = 'left', width?: string): React.CSSProperties => ({
        padding: '12px 10px',
        fontSize: '11px',
        color: THEME.text.tertiary,
        fontWeight: 600,
        textAlign: align,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        width,
        position: 'sticky',
        top: 0,
        backgroundColor: THEME.bg.tertiary,
        borderBottom: `2px solid ${THEME.border.primary}`,
    });

    // Table cell style
    const tdStyle = (align: 'left' | 'center' | 'right' = 'left'): React.CSSProperties => ({
        padding: '12px 10px',
        textAlign: align,
        fontSize: '12px',
    });

    if (isLoading && !trades) {
        return (
            <div style={containerStyle}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ height: '20px', backgroundColor: THEME.bg.vessel, borderRadius: '4px', width: '200px' }}></div>
                    {[...Array(5)].map((_, i) => (
                        <div key={i} style={{ height: '52px', backgroundColor: THEME.bg.vessel, borderRadius: '4px' }}></div>
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
                paddingBottom: '16px',
                borderBottom: `1px solid ${THEME.border.primary}`,
                marginBottom: '16px'
            }}>
                <h2 style={{
                    fontSize: '18px',
                    fontWeight: 700,
                    color: THEME.text.primary,
                    margin: 0,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}>
                    📋 Lịch sử giao dịch
                </h2>
                <span style={{
                    fontSize: '12px',
                    color: THEME.text.tertiary,
                    backgroundColor: THEME.bg.vessel,
                    padding: '4px 12px',
                    borderRadius: '12px',
                }}>
                    {trades?.total || 0} giao dịch
                </span>
            </div>

            {/* Table */}
            {trades?.trades.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '48px', color: THEME.text.tertiary }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    Chưa có giao dịch nào
                </div>
            ) : (
                <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
                        <thead>
                            <tr>
                                <th style={thStyle('left', '100px')}>Thời gian</th>
                                <th style={thStyle('left', '90px')}>Cặp</th>
                                <th style={thStyle('center', '70px')}>Loại</th>
                                <th style={thStyle('right', '100px')}>Entry</th>
                                <th style={thStyle('right', '100px')}>Exit</th>
                                <th style={thStyle('right', '140px')}>P&L</th>
                                <th style={thStyle('center', '80px')}>Thời lượng</th>
                                <th style={thStyle('center', '100px')}>Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trades?.trades.map((trade, index) => {
                                const exitPrice = calculateExitPrice(trade);
                                const pnlPercent = calculatePnlPercent(trade);
                                const isProfitable = trade.realized_pnl >= 0;

                                return (
                                    <tr
                                        key={trade.id}
                                        style={{
                                            borderBottom: `1px solid ${THEME.border.secondary}`,
                                            backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(30,35,41,0.3)',
                                            transition: 'background-color 0.15s',
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(240,185,11,0.05)'}
                                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = index % 2 === 0 ? 'transparent' : 'rgba(30,35,41,0.3)'}
                                    >
                                        {/* Time */}
                                        <td style={{ ...tdStyle('left'), fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: THEME.text.secondary }}>
                                            {formatVietnamDate(trade.close_time || trade.open_time)}
                                        </td>

                                        {/* Symbol - SOTA: Always uppercase */}
                                        <td style={{ ...tdStyle('left'), fontWeight: 700, color: THEME.text.primary }}>
                                            {trade.symbol.toUpperCase()}
                                        </td>

                                        {/* Side */}
                                        <td style={tdStyle('center')}>
                                            <span style={{
                                                display: 'inline-block',
                                                padding: '4px 10px',
                                                borderRadius: '4px',
                                                fontSize: '10px',
                                                fontWeight: 700,
                                                backgroundColor: trade.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                                color: trade.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                            }}>
                                                {trade.side === 'LONG' ? 'MUA' : 'BÁN'}
                                            </span>
                                        </td>

                                        {/* Entry Price */}
                                        <td style={{ ...tdStyle('right'), fontFamily: "'JetBrains Mono', monospace", color: THEME.text.primary }}>
                                            ${formatPrice(trade.entry_price)}
                                        </td>

                                        {/* Exit Price - SOTA: Calculated */}
                                        <td style={{ ...tdStyle('right'), fontFamily: "'JetBrains Mono', monospace", color: THEME.text.secondary }}>
                                            {exitPrice !== null ? `$${formatPrice(exitPrice)}` : '-'}
                                        </td>

                                        {/* P&L - SOTA: Both $ and % */}
                                        <td style={{ ...tdStyle('right') }}>
                                            <div style={{
                                                display: 'flex',
                                                flexDirection: 'column',
                                                alignItems: 'flex-end',
                                                gap: '2px'
                                            }}>
                                                <span style={{
                                                    fontFamily: "'JetBrains Mono', monospace",
                                                    fontWeight: 700,
                                                    color: isProfitable ? THEME.status.buy : THEME.status.sell
                                                }}>
                                                    {isProfitable ? '+' : ''}{formatPrice(trade.realized_pnl)}
                                                </span>
                                                <span style={{
                                                    fontFamily: "'JetBrains Mono', monospace",
                                                    fontSize: '10px',
                                                    color: isProfitable ? THEME.status.buy : THEME.status.sell,
                                                    opacity: 0.8
                                                }}>
                                                    ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                                                </span>
                                            </div>
                                        </td>

                                        {/* Duration */}
                                        <td style={{ ...tdStyle('center'), fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: THEME.text.tertiary }}>
                                            {calculateDuration(trade.open_time, trade.close_time)}
                                        </td>

                                        {/* Exit Reason */}
                                        <td style={tdStyle('center')}>
                                            {getExitReasonBadge(trade.exit_reason)}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Pagination - SOTA: Page numbers */}
            {trades && trades.total_pages > 1 && (
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginTop: '16px',
                    paddingTop: '16px',
                    borderTop: `1px solid ${THEME.border.primary}`
                }}>
                    <span style={{ fontSize: '12px', color: THEME.text.tertiary }}>
                        Trang {trades.page} / {trades.total_pages}
                    </span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                        {/* Previous */}
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            style={{
                                padding: '8px 12px',
                                fontSize: '12px',
                                borderRadius: '4px',
                                border: 'none',
                                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                backgroundColor: THEME.bg.vessel,
                                color: THEME.text.secondary,
                                opacity: currentPage === 1 ? 0.5 : 1,
                            }}
                        >
                            ←
                        </button>

                        {/* Page Numbers */}
                        {(() => {
                            const pages = [];
                            const totalPages = trades.total_pages;
                            const current = currentPage;

                            // Calculate visible page range
                            let start = Math.max(1, current - 2);
                            let end = Math.min(totalPages, start + 4);
                            start = Math.max(1, end - 4);

                            for (let i = start; i <= end; i++) {
                                pages.push(
                                    <button
                                        key={i}
                                        onClick={() => setCurrentPage(i)}
                                        style={{
                                            padding: '8px 12px',
                                            fontSize: '12px',
                                            fontWeight: currentPage === i ? 700 : 400,
                                            borderRadius: '4px',
                                            border: 'none',
                                            cursor: 'pointer',
                                            backgroundColor: currentPage === i ? THEME.accent.yellow : THEME.bg.vessel,
                                            color: currentPage === i ? '#000' : THEME.text.secondary,
                                            minWidth: '36px',
                                        }}
                                    >
                                        {i}
                                    </button>
                                );
                            }
                            return pages;
                        })()}

                        {/* Next */}
                        <button
                            onClick={() => setCurrentPage(p => Math.min(trades.total_pages, p + 1))}
                            disabled={currentPage === trades.total_pages}
                            style={{
                                padding: '8px 12px',
                                fontSize: '12px',
                                borderRadius: '4px',
                                border: 'none',
                                cursor: currentPage === trades.total_pages ? 'not-allowed' : 'pointer',
                                backgroundColor: THEME.bg.vessel,
                                color: THEME.text.secondary,
                                opacity: currentPage === trades.total_pages ? 0.5 : 1,
                            }}
                        >
                            →
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TradeHistory;
