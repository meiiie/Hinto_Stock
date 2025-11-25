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
 * Trade History Component - Binance Style
 * Displays paginated trade history with Vietnam timezone
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
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium" style={{ backgroundColor: c.bg, color: c.color }}>
                {c.label}
            </span>
        );
    };

    if (isLoading && !trades) {
        return (
            <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
                <div className="animate-pulse space-y-3">
                    <div className="h-4 rounded w-1/3" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-12 rounded" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    ))}
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

    return (
        <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
            {/* Header */}
            <div className="flex justify-between items-center pb-3 mb-4" style={{ borderBottom: `1px solid ${THEME.border.primary}` }}>
                <h2 className="text-lg font-bold" style={{ color: THEME.text.primary }}>Lịch sử giao dịch</h2>
                <span className="text-xs" style={{ color: THEME.text.tertiary }}>
                    {trades?.total || 0} giao dịch
                </span>
            </div>

            {/* Table */}
            {trades?.trades.length === 0 ? (
                <div className="text-center py-8" style={{ color: THEME.text.tertiary }}>
                    Chưa có giao dịch nào
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr style={{ borderBottom: `1px solid ${THEME.border.primary}` }}>
                                <th className="text-left py-2 px-2" style={{ color: THEME.text.tertiary }}>Thời gian</th>
                                <th className="text-left py-2 px-2" style={{ color: THEME.text.tertiary }}>Cặp</th>
                                <th className="text-left py-2 px-2" style={{ color: THEME.text.tertiary }}>Loại</th>
                                <th className="text-right py-2 px-2" style={{ color: THEME.text.tertiary }}>Entry</th>
                                <th className="text-right py-2 px-2" style={{ color: THEME.text.tertiary }}>Exit</th>
                                <th className="text-right py-2 px-2" style={{ color: THEME.text.tertiary }}>P&L</th>
                                <th className="text-center py-2 px-2" style={{ color: THEME.text.tertiary }}>Thời lượng</th>
                                <th className="text-center py-2 px-2" style={{ color: THEME.text.tertiary }}>Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trades?.trades.map((trade) => (
                                <tr key={trade.id} className="hover:opacity-80" style={{ borderBottom: `1px solid ${THEME.border.secondary}` }}>
                                    <td className="py-2 px-2 font-mono" style={{ color: THEME.text.secondary }}>
                                        {formatVietnamDate(trade.close_time || trade.open_time)}
                                    </td>
                                    <td className="py-2 px-2 font-semibold" style={{ color: THEME.text.primary }}>
                                        {trade.symbol}
                                    </td>
                                    <td className="py-2 px-2">
                                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold" style={{
                                            backgroundColor: trade.side === 'LONG' ? THEME.alpha.buyBg : THEME.alpha.sellBg,
                                            color: trade.side === 'LONG' ? THEME.status.buy : THEME.status.sell
                                        }}>
                                            {trade.side === 'LONG' ? 'MUA' : 'BÁN'}
                                        </span>
                                    </td>
                                    <td className="py-2 px-2 text-right font-mono" style={{ color: THEME.text.secondary }}>
                                        ${formatPrice(trade.entry_price)}
                                    </td>
                                    <td className="py-2 px-2 text-right font-mono" style={{ color: THEME.text.secondary }}>
                                        {trade.exit_reason === 'TAKE_PROFIT' ? `$${formatPrice(trade.take_profit)}` :
                                         trade.exit_reason === 'STOP_LOSS' ? `$${formatPrice(trade.stop_loss)}` : '-'}
                                    </td>
                                    <td className="py-2 px-2 text-right font-mono font-bold" style={{ color: trade.realized_pnl >= 0 ? THEME.status.buy : THEME.status.sell }}>
                                        {trade.realized_pnl >= 0 ? '+' : ''}{formatPrice(trade.realized_pnl)}
                                    </td>
                                    <td className="py-2 px-2 text-center font-mono" style={{ color: THEME.text.tertiary }}>
                                        {calculateDuration(trade.open_time, trade.close_time)}
                                    </td>
                                    <td className="py-2 px-2 text-center">
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
                <div className="flex justify-between items-center mt-4 pt-3" style={{ borderTop: `1px solid ${THEME.border.primary}` }}>
                    <span className="text-xs" style={{ color: THEME.text.tertiary }}>
                        Trang {trades.page} / {trades.total_pages}
                    </span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="px-3 py-1 text-xs rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{ backgroundColor: THEME.bg.vessel, color: THEME.text.secondary }}
                        >
                            Trước
                        </button>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(trades.total_pages, p + 1))}
                            disabled={currentPage === trades.total_pages}
                            className="px-3 py-1 text-xs rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{ backgroundColor: THEME.bg.vessel, color: THEME.text.secondary }}
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
