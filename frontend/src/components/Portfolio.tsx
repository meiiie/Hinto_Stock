import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { formatPrice } from '../styles/theme';
import { apiUrl, ENDPOINTS } from '../config/api';
import { TokenIcon } from './TokenIcon';
import { ChevronDown, ChevronUp, XCircle, Briefcase, Clock, ChevronLeft, ChevronRight } from 'lucide-react';
import useMarketStore from '../stores/marketStore';

// --- INTERFACES ---
interface Position {
    id: string;
    symbol: string;
    side: 'LONG' | 'SHORT';
    status: string;
    entry_price: number;
    quantity: number;
    leverage: number;
    margin: number;
    stop_loss: number;
    take_profit: number;
    entry_time?: string;
    unrealized_pnl: number;
    roe_pct: number;
    current_price: number;
    current_value: number;
    size?: number;
}

interface PendingOrder {
    id: string;
    symbol: string;
    side: 'LONG' | 'SHORT';
    entry_price: number;
    size: number;
    quantity?: number;
    stop_loss: number;
    take_profits?: number[];
    take_profit?: number;
    created_at?: string;
    open_time?: string;
    margin?: number;
    leverage?: number;
}

interface PortfolioData {
    wallet_balance: number;
    margin_balance: number;
    available_balance: number;
    unrealized_pnl: number;
    total_equity: number;
    open_positions: Position[];
    pending_orders: PendingOrder[];
    realized_pnl: number;
}

// --- COLORS (Hinto Pro Style - Synced with Project) ---
const COLORS = {
    buy: 'rgb(14, 203, 129)',
    sell: 'rgb(246, 70, 93)',
    yellow: 'rgb(240, 185, 11)',
    bgPrimary: 'rgb(24, 26, 32)',      // Project standard
    bgSecondary: 'rgb(30, 35, 41)',
    bgTertiary: 'rgb(43, 49, 57)',
    textPrimary: 'rgb(234, 236, 239)',
    textSecondary: 'rgb(132, 142, 156)',
    textTertiary: 'rgb(94, 102, 115)',
};

// --- STYLES ---
const glassContainer: React.CSSProperties = {
    background: COLORS.bgPrimary, // Solid background - synced with project
    border: `1px solid ${COLORS.bgTertiary}`,
    borderRadius: '12px',
    padding: '20px',
    height: '100%',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
};

const thStyle = (align: 'left' | 'center' | 'right' = 'left'): React.CSSProperties => ({
    padding: '10px 8px',
    fontSize: '10px',
    color: COLORS.textTertiary,
    fontWeight: 600,
    textAlign: align,
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    background: COLORS.bgSecondary,
    borderBottom: `1px solid ${COLORS.bgTertiary}`,
    position: 'sticky' as const,
    top: 0,
    zIndex: 1,
});

const tdStyle = (align: 'left' | 'center' | 'right' = 'left'): React.CSSProperties => ({
    padding: '12px 8px',
    textAlign: align,
    fontSize: '12px',
});

const ITEMS_PER_PAGE = 10;

// --- SUB-COMPONENTS ---

// 1. Portfolio Row (Realtime SOTA)
// Extracts logic to dedicated component to prevent table re-renders
// and allows individual rows to subscribe to high-frequency price updates.
const PortfolioRow = React.memo(({ pos, index, onClose }: { pos: Position, index: number, onClose: (id: string) => void }) => {
    // SOTA: Subscribe to store for this specific symbol
    // This triggers re-render ONLY for this row when price changes.
    const liveClose = useMarketStore(state =>
        state.symbolData[pos.symbol.toLowerCase()]?.data1m?.close
    );

    // Determines the price source: Live Socket > API Snapshot > Entry (Fallback)
    const currentPrice = liveClose || (pos.current_price && !isNaN(pos.current_price) ? pos.current_price : pos.entry_price);

    // Calculate PnL locally for instant updates without waiting for backend
    // Formula: (Current - Entry) * Size * SideMultiplier
    const sideMultiplier = pos.side === 'LONG' ? 1 : -1;
    const sz = pos.size || pos.quantity || 0;

    // Use backend PnL if available and no live price, otherwise calculate
    const rawPnl = (currentPrice - pos.entry_price) * sz * sideMultiplier;
    const pnl = liveClose ? rawPnl : (pos.unrealized_pnl || rawPnl);

    // ROE Calculation
    const margin = pos.margin || (pos.entry_price * sz / pos.leverage);
    const roe = margin > 0 ? (pnl / margin) * 100 : 0;

    const sideColor = pos.side === 'LONG' ? COLORS.buy : COLORS.sell;
    const pnlColor = pnl >= 0 ? COLORS.buy : COLORS.sell;
    const tp = pos.take_profit || 0;
    const sl = pos.stop_loss || 0;

    return (
        <tr style={{ borderBottom: `1px solid ${COLORS.bgTertiary}30`, background: index % 2 === 0 ? 'transparent' : `${COLORS.bgSecondary}50`, color: COLORS.textPrimary }}>
            <td style={tdStyle('left')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TokenIcon symbol={pos.symbol.replace('USDT', '')} size={18} />
                    <div><div style={{ fontWeight: 700 }}>{pos.symbol.toUpperCase()}</div>
                        <span style={{ fontSize: '10px', color: sideColor, fontWeight: 700 }}>{pos.side} {pos.leverage || 1}x</span>
                    </div>
                </div>
            </td>
            <td style={{ ...tdStyle('right'), fontFamily: 'monospace', fontSize: '11px' }}>{sz.toFixed(4)}</td>
            <td style={{ ...tdStyle('right'), fontFamily: 'monospace', fontSize: '11px' }}>${formatPrice(pos.entry_price)}</td>
            <td style={{ ...tdStyle('right'), fontFamily: 'monospace', fontSize: '11px', color: liveClose ? COLORS.textPrimary : COLORS.textTertiary }}>
                ${formatPrice(currentPrice)}
            </td>
            <td style={{ ...tdStyle('right'), fontFamily: 'monospace', fontSize: '11px' }}>${margin.toFixed(2)}</td>
            <td style={{ ...tdStyle('right'), fontSize: '10px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px' }}>
                    <span style={{ color: COLORS.buy }}>{tp > 0 ? `$${formatPrice(tp)}` : '--'}</span>
                    <span style={{ color: COLORS.sell }}>{sl > 0 ? `$${formatPrice(sl)}` : '--'}</span>
                </div>
            </td>
            <td style={tdStyle('right')}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: pnlColor, fontSize: '12px' }}>{pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}</span>
                    <span style={{ fontFamily: 'monospace', fontSize: '10px', color: pnlColor }}>{roe.toFixed(2)}%</span>
                </div>
            </td>
            <td style={tdStyle('center')}><button onClick={() => onClose(pos.id)} style={{ padding: '4px 10px', fontSize: '10px', fontWeight: 600, borderRadius: '4px', border: `1px solid ${COLORS.bgTertiary}`, background: 'transparent', color: COLORS.textSecondary, cursor: 'pointer' }}>Close</button></td>
        </tr>
    );
});

const Portfolio: React.FC = () => {
    const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isPendingExpanded, setIsPendingExpanded] = useState(true);
    const [pendingPage, setPendingPage] = useState(1);
    const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null);

    const fetchPortfolio = useCallback(async () => {
        try {
            const response = await fetch(apiUrl(ENDPOINTS.PORTFOLIO));
            if (!response.ok) throw new Error('Failed to fetch');
            const data = await response.json();
            setPortfolio({
                wallet_balance: data.balance ?? data.wallet_balance,
                margin_balance: data.equity ?? data.margin_balance,
                available_balance: data.balance,
                unrealized_pnl: data.unrealized_pnl,
                total_equity: data.equity,
                realized_pnl: data.realized_pnl,
                open_positions: data.open_positions || [],
                pending_orders: data.pending_orders || []
            });
            setError(null);
        } catch (err) {
            console.error(err);
            setError('Unable to load portfolio');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        const interval = setInterval(fetchPortfolio, 3000);
        return () => clearInterval(interval);
    }, [fetchPortfolio]);

    const handleClosePosition = async (id: string) => {
        await fetch(apiUrl(ENDPOINTS.CLOSE_POSITION(id)), { method: 'POST' });
        fetchPortfolio();
    };

    const handleCloseAll = async () => {
        if (!portfolio?.open_positions.length) return;
        if (!confirm(`Close all ${portfolio.open_positions.length} positions?`)) return;
        for (const p of portfolio.open_positions) {
            await fetch(apiUrl(ENDPOINTS.CLOSE_POSITION(p.id)), { method: 'POST' });
        }
        fetchPortfolio();
    };

    // SOTA: Cancel single pending order
    const handleCancelPendingOrder = async (orderId: string) => {
        try {
            const response = await fetch(apiUrl(ENDPOINTS.CANCEL_PENDING_ORDER(orderId)), { method: 'DELETE' });
            if (response.ok) {
                fetchPortfolio();
            }
        } catch (err) {
            console.error('Failed to cancel pending order:', err);
        }
    };

    // SOTA: Cancel all pending orders
    const handleCancelAllPending = async () => {
        if (!pendingOrders.length) return;
        if (!confirm(`Cancel all ${pendingOrders.length} pending orders?`)) return;
        try {
            const response = await fetch(apiUrl(ENDPOINTS.CANCEL_ALL_PENDING), { method: 'DELETE' });
            if (response.ok) {
                fetchPortfolio();
            }
        } catch (err) {
            console.error('Failed to cancel all pending orders:', err);
        }
    };

    // Pagination logic for Pending Orders
    const pendingOrders = portfolio?.pending_orders || [];
    const totalPendingPages = Math.max(1, Math.ceil(pendingOrders.length / ITEMS_PER_PAGE));
    const paginatedPending = useMemo(() => {
        const start = (pendingPage - 1) * ITEMS_PER_PAGE;
        return pendingOrders.slice(start, start + ITEMS_PER_PAGE);
    }, [pendingOrders, pendingPage]);

    // Loading / Error
    if (isLoading && !portfolio) {
        return (
            <div style={glassContainer}>
                <SkeletonLoader />
            </div>
        );
    }
    if (error) return <div style={{ ...glassContainer, color: COLORS.sell }}>{error}</div>;

    return (
        <div style={glassContainer}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: `1px solid ${COLORS.bgTertiary}`, marginBottom: '16px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: 700, color: COLORS.textPrimary, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Briefcase size={18} style={{ color: COLORS.yellow }} /> Portfolio
                </h2>
                {portfolio?.open_positions && portfolio.open_positions.length > 0 && (
                    <button onClick={handleCloseAll} style={{ padding: '6px 12px', fontSize: '11px', fontWeight: 600, borderRadius: '6px', border: `1px solid ${COLORS.sell}40`, background: `${COLORS.sell}15`, color: COLORS.sell, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <XCircle size={12} /> Close All
                    </button>
                )}
            </div>

            {/* Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
                <MetricCard label="Wallet Balance" value={`$${formatPrice(portfolio?.wallet_balance || 0)}`} />
                <MetricCard label="Unrealized PNL" value={`$${(portfolio?.unrealized_pnl || 0).toFixed(2)}`} pnl={portfolio?.unrealized_pnl} />
                <MetricCard label="Equity" value={`$${formatPrice(portfolio?.total_equity || 0)}`} />
                <MetricCard label="Realized PNL" value={`$${(portfolio?.realized_pnl || 0).toFixed(2)}`} pnl={portfolio?.realized_pnl} />
            </div>

            {/* Positions Table - FIXED HEIGHT to prevent CLS */}
            <div style={{ minHeight: '250px', maxHeight: '300px', overflowY: 'auto', marginBottom: '16px', background: COLORS.bgPrimary, borderRadius: '8px', border: `1px solid ${COLORS.bgTertiary}` }}>
                {(!portfolio?.open_positions || portfolio.open_positions.length === 0) ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '200px', color: COLORS.textTertiary }}>
                        <Briefcase size={32} style={{ marginBottom: '12px', opacity: 0.2 }} />
                        <div style={{ fontSize: '13px' }}>No open positions</div>
                    </div>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead><tr>
                            <th style={thStyle('left')}>Symbol</th>
                            <th style={thStyle('right')}>Size</th>
                            <th style={thStyle('right')}>Entry</th>
                            <th style={thStyle('right')}>Mark</th>
                            <th style={thStyle('right')}>Margin</th>
                            <th style={thStyle('right')}>TP / SL</th>
                            <th style={thStyle('right')}>PnL (ROE)</th>
                            <th style={thStyle('center')}>Action</th>
                        </tr></thead>
                        <tbody>
                            {portfolio.open_positions.map((pos, i) => (
                                <PortfolioRow
                                    key={pos.id}
                                    pos={pos}
                                    index={i}
                                    onClose={handleClosePosition}
                                />
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Collapsible Pending Orders */}
            <div style={{ borderTop: `1px solid ${COLORS.bgTertiary}`, paddingTop: '16px', flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                <div onClick={() => setIsPendingExpanded(!isPendingExpanded)} style={{ fontSize: '13px', fontWeight: 600, color: COLORS.textSecondary, margin: 0, display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '12px', flex: 1 }}>
                    {isPendingExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    <Clock size={14} style={{ color: COLORS.yellow }} /> Pending Orders ({pendingOrders.length})
                </div>
                {pendingOrders.length > 0 && (
                    <button onClick={handleCancelAllPending} style={{ padding: '4px 10px', fontSize: '10px', fontWeight: 600, borderRadius: '4px', border: `1px solid ${COLORS.sell}40`, background: `${COLORS.sell}15`, color: COLORS.sell, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <XCircle size={12} /> Cancel All
                    </button>
                )}
            </div>

            {isPendingExpanded && (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                    {/* Fixed height container - PREVENTS CLS */}
                    <div style={{ minHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {pendingOrders.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '40px', color: COLORS.textTertiary, fontSize: '12px' }}>No pending orders</div>
                        ) : (
                            paginatedPending.map(order => (
                                <PendingOrderCard
                                    key={order.id}
                                    order={order}
                                    isExpanded={expandedOrderId === order.id}
                                    onToggle={() => setExpandedOrderId(expandedOrderId === order.id ? null : order.id)}
                                    onCancel={() => handleCancelPendingOrder(order.id)}
                                />
                            ))
                        )}
                    </div>

                    {/* Pagination */}
                    {totalPendingPages > 1 && (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '12px', paddingTop: '12px', borderTop: `1px solid ${COLORS.bgTertiary}` }}>
                            <button onClick={() => setPendingPage(p => Math.max(1, p - 1))} disabled={pendingPage === 1} style={{ padding: '6px 10px', borderRadius: '4px', border: 'none', background: COLORS.bgTertiary, color: COLORS.textSecondary, cursor: pendingPage === 1 ? 'not-allowed' : 'pointer', opacity: pendingPage === 1 ? 0.5 : 1 }}><ChevronLeft size={14} /></button>
                            <span style={{ fontSize: '12px', color: COLORS.textSecondary }}>{pendingPage} / {totalPendingPages}</span>
                            <button onClick={() => setPendingPage(p => Math.min(totalPendingPages, p + 1))} disabled={pendingPage === totalPendingPages} style={{ padding: '6px 10px', borderRadius: '4px', border: 'none', background: COLORS.bgTertiary, color: COLORS.textSecondary, cursor: pendingPage === totalPendingPages ? 'not-allowed' : 'pointer', opacity: pendingPage === totalPendingPages ? 0.5 : 1 }}><ChevronRight size={14} /></button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

// --- Pending Order Card (SignalCard-style) ---
const PendingOrderCard = ({ order, isExpanded, onToggle, onCancel }: { order: PendingOrder; isExpanded: boolean; onToggle: () => void; onCancel: () => void }) => {
    const sideColor = order.side === 'LONG' ? COLORS.buy : COLORS.sell;
    const sz = order.size || order.quantity || 0;
    const sl = order.stop_loss || 0;
    const tp1 = order.take_profit || (order.take_profits?.[0]) || 0;
    const tp2 = order.take_profits?.[1] || 0;

    return (
        <div style={{
            background: COLORS.bgSecondary,
            borderRadius: '8px',
            border: `1px solid ${sideColor}`,
            overflow: 'hidden',
            boxShadow: `0 0 15px ${sideColor}30`,
        }}>
            {/* Header (Always Visible) */}
            <div onClick={onToggle} style={{
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: `${sideColor}15`,
                cursor: 'pointer',
                borderBottom: isExpanded ? `1px solid ${COLORS.bgTertiary}` : 'none',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: sideColor, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 700, fontSize: '14px' }}>
                        {order.side === 'LONG' ? '↑' : '↓'}
                    </div>
                    <div>
                        <div style={{ fontSize: '14px', fontWeight: 700, color: sideColor, display: 'flex', alignItems: 'center', gap: '8px' }}>
                            {order.side} {order.symbol.toUpperCase()}
                            <span style={{ fontSize: '9px', padding: '2px 6px', borderRadius: '4px', background: COLORS.bgTertiary, color: COLORS.textSecondary }}>Pending</span>
                        </div>
                        <div style={{ fontSize: '11px', color: COLORS.textTertiary }}>{order.created_at || order.open_time || '--'}</div>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '13px', color: COLORS.textPrimary, fontWeight: 600 }}>@${order.entry_price.toFixed(2)}</span>
                    <button
                        onClick={(e) => { e.stopPropagation(); onCancel(); }}
                        style={{
                            padding: '4px 8px',
                            fontSize: '10px',
                            fontWeight: 600,
                            borderRadius: '4px',
                            border: `1px solid ${COLORS.sell}40`,
                            background: `${COLORS.sell}15`,
                            color: COLORS.sell,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                        }}
                    >
                        <XCircle size={12} /> Cancel
                    </button>
                    <span style={{ color: COLORS.textTertiary, fontSize: '14px' }}>{isExpanded ? '▲' : '▼'}</span>
                </div>
            </div>

            {/* Body (Collapsible) */}
            {isExpanded && (
                <div style={{ padding: '16px' }}>
                    {/* Price Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '12px' }}>
                        <PriceItem label="Entry" value={`$${order.entry_price.toFixed(2)}`} color={COLORS.yellow} />
                        <PriceItem label="Stop Loss" value={sl > 0 ? `$${sl.toFixed(2)}` : '--'} color={COLORS.sell} />
                        <PriceItem label="TP1" value={tp1 > 0 ? `$${tp1.toFixed(2)}` : '--'} color={COLORS.buy} />
                        <PriceItem label="TP2" value={tp2 > 0 ? `$${tp2.toFixed(2)}` : '--'} color={COLORS.buy} />
                    </div>

                    {/* Details Row */}
                    <div style={{ display: 'flex', justifyContent: 'space-around', padding: '10px', background: COLORS.bgPrimary, borderRadius: '6px', fontSize: '11px' }}>
                        <div style={{ textAlign: 'center' }}><div style={{ color: COLORS.textTertiary, marginBottom: '2px' }}>Size</div><div style={{ color: COLORS.textPrimary, fontWeight: 600, fontFamily: 'monospace' }}>{sz.toFixed(4)}</div></div>
                        <div style={{ textAlign: 'center' }}><div style={{ color: COLORS.textTertiary, marginBottom: '2px' }}>Margin</div><div style={{ color: COLORS.textPrimary, fontWeight: 600, fontFamily: 'monospace' }}>${(order.margin || 0).toFixed(2)}</div></div>
                        <div style={{ textAlign: 'center' }}><div style={{ color: COLORS.textTertiary, marginBottom: '2px' }}>Leverage</div><div style={{ color: COLORS.textPrimary, fontWeight: 600 }}>{order.leverage || 1}x</div></div>
                    </div>
                </div>
            )}
        </div>
    );
};

const PriceItem = ({ label, value, color }: { label: string; value: string; color: string }) => (
    <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '10px', color: COLORS.textTertiary, marginBottom: '4px' }}>{label}</div>
        <div style={{ fontSize: '13px', fontWeight: 700, color, fontFamily: 'monospace' }}>{value}</div>
    </div>
);

const MetricCard = ({ label, value, pnl }: { label: string; value: string; pnl?: number }) => {
    const color = pnl !== undefined ? (pnl >= 0 ? COLORS.buy : COLORS.sell) : COLORS.textPrimary;
    return (
        <div style={{ background: COLORS.bgSecondary, borderRadius: '6px', padding: '12px', border: `1px solid ${COLORS.bgTertiary}` }}>
            <div style={{ fontSize: '10px', color: COLORS.textTertiary, marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</div>
            <div style={{ fontSize: '14px', fontWeight: 700, color, fontFamily: 'monospace' }}>{value}</div>
        </div>
    );
};

const SkeletonLoader = () => (
    <>
        <div style={{ height: '24px', background: COLORS.bgSecondary, borderRadius: '4px', width: '150px', marginBottom: '16px' }}></div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
            {[...Array(4)].map((_, i) => <div key={i} style={{ height: '50px', background: COLORS.bgSecondary, borderRadius: '6px' }}></div>)}
        </div>
        <div style={{ height: '200px', background: COLORS.bgSecondary, borderRadius: '8px' }}></div>
    </>
);

export default Portfolio;
