import React, { useState, useEffect, useCallback } from 'react';
import { THEME, formatPrice } from '../styles/theme';

interface PerformanceMetrics {
    total_pnl: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    avg_win: number;
    avg_loss: number;
    profit_factor: number;
    max_drawdown: number;
    largest_win: number;
    largest_loss: number;
}

type Period = '7d' | '30d' | '90d' | 'all';

/**
 * Performance Dashboard Component - Binance Style
 * Displays win rate, profit factor, max drawdown, total PnL
 */
const PerformanceDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
    const [period, setPeriod] = useState<Period>('7d');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const periodDays: Record<Period, number> = { '7d': 7, '30d': 30, '90d': 90, 'all': 365 };
    const periodLabels: Record<Period, string> = { '7d': '7 ngày', '30d': '30 ngày', '90d': '90 ngày', 'all': 'Tất cả' };

    const fetchMetrics = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/trades/performance?days=${periodDays[period]}`);
            if (!response.ok) throw new Error('Failed to fetch metrics');
            const data = await response.json();
            setMetrics(data);
            setError(null);
        } catch (err) {
            setError('Không thể tải dữ liệu hiệu suất');
        } finally {
            setIsLoading(false);
        }
    }, [period]);

    useEffect(() => {
        fetchMetrics();
    }, [fetchMetrics]);

    const MetricCard: React.FC<{
        label: string;
        value: string | number;
        subValue?: string;
        color?: 'buy' | 'sell' | 'warning' | 'info' | 'primary';
        large?: boolean;
    }> = ({ label, value, subValue, color = 'primary', large = false }) => {
        const colorMap = {
            buy: THEME.status.buy,
            sell: THEME.status.sell,
            warning: THEME.accent.yellow,
            info: THEME.status.info,
            primary: THEME.text.primary,
        };
        return (
            <div className="rounded p-3" style={{ backgroundColor: THEME.bg.vessel }}>
                <div className="text-xs mb-1" style={{ color: THEME.text.tertiary }}>{label}</div>
                <div className={`${large ? 'text-2xl' : 'text-lg'} font-bold font-mono`} style={{ color: colorMap[color] }}>
                    {value}
                </div>
                {subValue && <div className="text-xs mt-1" style={{ color: THEME.text.tertiary }}>{subValue}</div>}
            </div>
        );
    };

    if (isLoading && !metrics) {
        return (
            <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
                <div className="animate-pulse space-y-3">
                    <div className="h-4 rounded w-1/3" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    <div className="grid grid-cols-4 gap-3">
                        {[...Array(8)].map((_, i) => (
                            <div key={i} className="h-20 rounded" style={{ backgroundColor: THEME.bg.vessel }}></div>
                        ))}
                    </div>
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

    const winRate = metrics?.win_rate || 0;
    const profitFactor = metrics?.profit_factor || 0;
    const totalPnL = metrics?.total_pnl || 0;

    return (
        <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
            {/* Header with Period Selector */}
            <div className="flex justify-between items-center pb-3 mb-4" style={{ borderBottom: `1px solid ${THEME.border.primary}` }}>
                <h2 className="text-lg font-bold" style={{ color: THEME.text.primary }}>Hiệu suất</h2>
                <div className="flex gap-1">
                    {(['7d', '30d', '90d', 'all'] as Period[]).map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className="px-2 py-1 text-xs rounded transition-colors"
                            style={{
                                backgroundColor: period === p ? THEME.accent.yellow : 'transparent',
                                color: period === p ? '#000' : THEME.text.secondary,
                            }}
                        >
                            {periodLabels[p]}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Metrics */}
            <div className="grid grid-cols-4 gap-3 mb-4">
                <MetricCard
                    label="Tổng P&L"
                    value={`${totalPnL >= 0 ? '+' : ''}${formatPrice(totalPnL)}`}
                    color={totalPnL >= 0 ? 'buy' : 'sell'}
                    large
                />
                <MetricCard
                    label="Tỷ lệ thắng"
                    value={`${(winRate * 100).toFixed(1)}%`}
                    subValue={`${metrics?.winning_trades || 0}W / ${metrics?.losing_trades || 0}L`}
                    color={winRate >= 0.5 ? 'buy' : 'warning'}
                    large
                />
                <MetricCard
                    label="Profit Factor"
                    value={profitFactor === Infinity ? '∞' : profitFactor.toFixed(2)}
                    color={profitFactor >= 1.5 ? 'buy' : profitFactor >= 1 ? 'warning' : 'sell'}
                    large
                />
                <MetricCard
                    label="Max Drawdown"
                    value={`-${formatPrice(metrics?.max_drawdown || 0)}`}
                    color="sell"
                    large
                />
            </div>

            {/* Secondary Metrics */}
            <div className="grid grid-cols-4 gap-3">
                <MetricCard label="Tổng giao dịch" value={metrics?.total_trades || 0} color="info" />
                <MetricCard label="TB Thắng" value={`+${formatPrice(metrics?.avg_win || 0)}`} color="buy" />
                <MetricCard label="TB Thua" value={`-${formatPrice(Math.abs(metrics?.avg_loss || 0))}`} color="sell" />
                <MetricCard label="Thắng lớn nhất" value={`+${formatPrice(metrics?.largest_win || 0)}`} color="buy" />
            </div>

            {/* Win Rate Progress Bar */}
            <div className="mt-4 pt-3" style={{ borderTop: `1px solid ${THEME.border.primary}` }}>
                <div className="flex justify-between text-xs mb-1" style={{ color: THEME.text.tertiary }}>
                    <span>Phân bố Thắng/Thua</span>
                    <span>{metrics?.winning_trades || 0} thắng / {metrics?.losing_trades || 0} thua</span>
                </div>
                <div className="h-2 rounded-full overflow-hidden flex" style={{ backgroundColor: THEME.bg.vessel }}>
                    <div className="h-full transition-all duration-300" style={{ width: `${winRate * 100}%`, backgroundColor: THEME.status.buy }} />
                    <div className="h-full transition-all duration-300" style={{ width: `${(1 - winRate) * 100}%`, backgroundColor: THEME.status.sell }} />
                </div>
            </div>

            {/* No Data Message */}
            {metrics?.total_trades === 0 && (
                <div className="text-center py-4 text-sm mt-4" style={{ color: THEME.text.tertiary }}>
                    Không có giao dịch trong khoảng thời gian đã chọn
                </div>
            )}
        </div>
    );
};

export default PerformanceDashboard;
