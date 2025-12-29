import React, { useState, useEffect, useCallback } from 'react';
import { THEME } from '../styles/theme';
import { apiUrl, ENDPOINTS } from '../config/api';

interface TradingSettings {
    risk_percent: number;
    rr_ratio: number;
    max_positions: number;
    leverage: number;
    auto_execute: boolean;
}

// SOTA Phase 26: Token Watchlist type
interface TokenWatchlistItem {
    symbol: string;
    enabled: boolean;
    alias: string | null;
}

/**
 * Settings Component - Binance Style with Inline Styles
 * SOTA Phase 26: Enhanced with Token Watchlist
 */
const Settings: React.FC = () => {
    const [settings, setSettings] = useState<TradingSettings>({
        risk_percent: 1.5,
        rr_ratio: 1.5,
        max_positions: 3,
        leverage: 1,
        auto_execute: false
    });
    const [tokenWatchlist, setTokenWatchlist] = useState<TokenWatchlistItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [isSimulating, setIsSimulating] = useState(false);

    const fetchSettings = useCallback(async () => {
        try {
            const response = await fetch(apiUrl(ENDPOINTS.SETTINGS));
            if (response.ok) {
                const data = await response.json();
                setSettings(data);
            }

            // SOTA Phase 26: Fetch token watchlist
            const tokensRes = await fetch(apiUrl(ENDPOINTS.TOKENS));
            if (tokensRes.ok) {
                const tokensData = await tokensRes.json();
                setTokenWatchlist(tokensData.tokens || []);
            }
        } catch (err) {
            setError('Không thể tải cài đặt');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    // SOTA Phase 26: Toggle token enabled/disabled
    const handleTokenToggle = async (symbol: string) => {
        const updatedTokens = tokenWatchlist.map(t =>
            t.symbol === symbol ? { ...t, enabled: !t.enabled } : t
        );
        setTokenWatchlist(updatedTokens);

        try {
            await fetch(apiUrl(ENDPOINTS.TOKENS), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tokens: updatedTokens })
            });
        } catch (err) {
            setError('Không thể cập nhật token');
        }
    };

    // SOTA Phase 26b: Add new token
    const [newTokenSymbol, setNewTokenSymbol] = useState('');
    const [isAddingToken, setIsAddingToken] = useState(false);
    const [activeTab, setActiveTab] = useState<'tokens' | 'risk' | 'strategy' | 'debug'>('tokens');
    const [searchResults, setSearchResults] = useState<string[]>([]);
    const [showSearchDropdown, setShowSearchDropdown] = useState(false);

    // Search tokens with debounce
    useEffect(() => {
        if (newTokenSymbol.length < 2) {
            setSearchResults([]);
            setShowSearchDropdown(false);
            return;
        }

        const timer = setTimeout(async () => {
            try {
                const res = await fetch(apiUrl(ENDPOINTS.TOKENS_SEARCH(newTokenSymbol, 10)));
                if (res.ok) {
                    const data = await res.json();
                    setSearchResults(data.symbols || []);
                    setShowSearchDropdown(data.symbols?.length > 0);
                }
            } catch (err) {
                setSearchResults([]);
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [newTokenSymbol]);

    const handleAddToken = async () => {
        if (!newTokenSymbol.trim()) return;

        setIsAddingToken(true);
        setError(null);

        try {
            // Validate with Binance API
            const validateRes = await fetch(apiUrl(ENDPOINTS.TOKENS_VALIDATE(newTokenSymbol)));
            const validateData = await validateRes.json();

            if (!validateData.valid) {
                setError(validateData.message);
                setIsAddingToken(false);
                return;
            }

            // Add token
            const addRes = await fetch(apiUrl(ENDPOINTS.TOKENS_ADD), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol: newTokenSymbol })
            });

            if (addRes.ok) {
                const data = await addRes.json();
                setTokenWatchlist(data.tokens || []);
                setNewTokenSymbol('');

                // SOTA: Notify user about backend restart requirement for streams
                alert(`✅ Đã thêm token ${newTokenSymbol} thành công!\n\n⚠️ Lưu ý: Cần restart backend để tạo stream mới.\nToken sẽ xuất hiện trong dropdown sau khi restart.`);
            } else {
                const err = await addRes.json();
                setError(err.detail || 'Không thể thêm token');
            }
        } catch (err) {
            setError('Lỗi khi thêm token');
        } finally {
            setIsAddingToken(false);
        }
    };

    const handleRemoveToken = async (symbol: string) => {
        if (!confirm(`Xóa token ${symbol}?`)) return;

        try {
            const res = await fetch(apiUrl(ENDPOINTS.TOKENS_REMOVE(symbol)), {
                method: 'DELETE'
            });

            if (res.ok) {
                const data = await res.json();
                setTokenWatchlist(data.tokens || []);
            } else {
                const err = await res.json();
                setError(err.detail || 'Không thể xóa token');
            }
        } catch (err) {
            setError('Lỗi khi xóa token');
        }
    };


    const handleSave = async () => {
        setIsSaving(true);
        setError(null);
        setSaveSuccess(false);
        try {
            const response = await fetch(apiUrl(ENDPOINTS.SETTINGS), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            if (response.ok) {
                setSaveSuccess(true);
                setTimeout(() => setSaveSuccess(false), 3000);
            } else {
                throw new Error('Failed to save');
            }
        } catch (err) {
            setError('Không thể lưu cài đặt');
        } finally {
            setIsSaving(false);
        }
    };

    const handleReset = async () => {
        if (!confirm('Reset tài khoản paper trading? Điều này sẽ xóa tất cả giao dịch và đặt lại số dư về $10,000.')) {
            return;
        }
        try {
            const response = await fetch(apiUrl(ENDPOINTS.RESET_TRADES), { method: 'POST' });
            if (response.ok) {
                alert('Đã reset tài khoản thành công!');
            }
        } catch (err) {
            setError('Không thể reset tài khoản');
        }
    };

    const handleSimulateSignal = async (signalType: 'BUY' | 'SELL') => {
        setIsSimulating(true);
        try {
            const response = await fetch(apiUrl(ENDPOINTS.SIMULATE_TRADE), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ signal_type: signalType })
            });
            if (response.ok) {
                const result = await response.json();
                alert(`✅ Đã tạo lệnh ${signalType} thành công!\nEntry: $${result.entry_price?.toFixed(2) || 'N/A'}`);
            } else {
                const err = await response.json();
                alert(`❌ Lỗi: ${err.detail || 'Không thể tạo lệnh'}`);
            }
        } catch (err) {
            setError('Không thể simulate signal');
        } finally {
            setIsSimulating(false);
        }
    };

    // Styles
    const containerStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.secondary,
        border: `1px solid ${THEME.border.primary}`,
        borderRadius: '8px',
        padding: '16px',
    };

    const sectionStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
    };

    const headerStyle: React.CSSProperties = {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingBottom: '12px',
        borderBottom: `1px solid ${THEME.border.primary}`,
        marginBottom: '16px',
    };

    const inputStyle: React.CSSProperties = {
        width: '100%',
        backgroundColor: THEME.bg.vessel,
        border: `1px solid ${THEME.border.input}`,
        color: THEME.text.primary,
        borderRadius: '4px',
        padding: '8px 12px',
        fontSize: '14px',
        outline: 'none',
    };

    const labelStyle: React.CSSProperties = {
        display: 'block',
        fontSize: '12px',
        color: THEME.text.tertiary,
        marginBottom: '4px',
    };

    const gridStyle: React.CSSProperties = {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
    };

    const cardStyle: React.CSSProperties = {
        backgroundColor: THEME.bg.vessel,
        borderRadius: '4px',
        padding: '8px',
    };

    const buttonStyle = (bg: string, color: string): React.CSSProperties => ({
        padding: '8px 16px',
        fontSize: '12px',
        fontWeight: 700,
        borderRadius: '4px',
        border: 'none',
        cursor: 'pointer',
        backgroundColor: bg,
        color: color,
        transition: 'opacity 0.2s',
    });

    if (isLoading) {
        return (
            <div style={containerStyle}>
                <div style={{ ...sectionStyle, gap: '16px' }}>
                    <div style={{ height: '16px', backgroundColor: THEME.bg.vessel, borderRadius: '4px', width: '33%' }}></div>
                    {[...Array(4)].map((_, i) => (
                        <div key={i} style={{ height: '40px', backgroundColor: THEME.bg.vessel, borderRadius: '4px' }}></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div style={containerStyle}>
            {/* Header */}
            <div style={headerStyle}>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: THEME.text.primary, margin: 0 }}>Bảng Điều Khiển</h2>
                {saveSuccess && (
                    <span style={{ fontSize: '12px', color: THEME.status.buy }}>✓ Đã lưu</span>
                )}
            </div>

            {/* SOTA Phase 26b: Tabbed Navigation with Professional SVG Icons */}
            <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', borderBottom: `1px solid ${THEME.border.primary}`, paddingBottom: '12px' }}>
                {[
                    {
                        key: 'tokens',
                        label: 'Token',
                        icon: (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M12 6v12M6 12h12" />
                            </svg>
                        )
                    },
                    {
                        key: 'risk',
                        label: 'Rủi ro',
                        icon: (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                                <line x1="12" y1="9" x2="12" y2="13" />
                                <line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                        )
                    },
                    {
                        key: 'strategy',
                        label: 'Chiến lược',
                        icon: (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="18" y1="20" x2="18" y2="10" />
                                <line x1="12" y1="20" x2="12" y2="4" />
                                <line x1="6" y1="20" x2="6" y2="14" />
                            </svg>
                        )
                    },
                    {
                        key: 'debug',
                        label: 'Debug',
                        icon: (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" />
                            </svg>
                        )
                    }
                ].map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as typeof activeTab)}
                        style={{
                            padding: '8px 16px',
                            fontSize: '12px',
                            fontWeight: 600,
                            borderRadius: '4px',
                            border: 'none',
                            cursor: 'pointer',
                            backgroundColor: activeTab === tab.key ? THEME.accent.yellow : 'transparent',
                            color: activeTab === tab.key ? '#000' : THEME.text.secondary,
                            transition: 'all 0.2s',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                        }}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content: Token Management */}
            {activeTab === 'tokens' && (
                <div style={sectionStyle}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>
                            Token Watchlist
                        </h3>
                        <span style={{ fontSize: '11px', color: THEME.text.tertiary }}>
                            {tokenWatchlist.filter(t => t.enabled).length}/{tokenWatchlist.length} đang bật
                        </span>
                    </div>

                    {/* Add Token Form with Search Dropdown */}
                    <div style={{ position: 'relative', margin: '12px 0' }}>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <input
                                type="text"
                                placeholder="Gõ để tìm token (VD: XRP, DOT...)"
                                value={newTokenSymbol}
                                onChange={(e) => setNewTokenSymbol(e.target.value.toUpperCase())}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleAddToken();
                                    if (e.key === 'Escape') setShowSearchDropdown(false);
                                }}
                                onFocus={() => searchResults.length > 0 && setShowSearchDropdown(true)}
                                onBlur={() => setTimeout(() => setShowSearchDropdown(false), 200)}
                                style={{
                                    flex: 1,
                                    padding: '8px 12px',
                                    fontSize: '12px',
                                    borderRadius: '4px',
                                    border: `1px solid ${THEME.border.input}`,
                                    backgroundColor: THEME.bg.vessel,
                                    color: THEME.text.primary,
                                    outline: 'none',
                                }}
                            />
                            <button
                                onClick={handleAddToken}
                                disabled={isAddingToken || !newTokenSymbol.trim()}
                                style={{
                                    padding: '8px 16px',
                                    fontSize: '12px',
                                    fontWeight: 600,
                                    borderRadius: '4px',
                                    border: 'none',
                                    cursor: newTokenSymbol.trim() ? 'pointer' : 'not-allowed',
                                    backgroundColor: THEME.status.buy,
                                    color: '#fff',
                                    opacity: newTokenSymbol.trim() ? 1 : 0.5,
                                }}
                            >
                                {isAddingToken ? '...' : '+ Thêm'}
                            </button>
                        </div>

                        {/* Search Dropdown */}
                        {showSearchDropdown && searchResults.length > 0 && (
                            <div style={{
                                position: 'absolute',
                                top: '100%',
                                left: 0,
                                right: 60,
                                backgroundColor: THEME.bg.vessel,
                                border: `1px solid ${THEME.border.primary}`,
                                borderRadius: '4px',
                                marginTop: '4px',
                                maxHeight: '200px',
                                overflowY: 'auto',
                                zIndex: 10,
                                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                            }}>
                                {searchResults.map((symbol) => (
                                    <div
                                        key={symbol}
                                        onClick={() => {
                                            setNewTokenSymbol(symbol);
                                            setShowSearchDropdown(false);
                                        }}
                                        style={{
                                            padding: '8px 12px',
                                            fontSize: '12px',
                                            color: THEME.text.primary,
                                            cursor: 'pointer',
                                            borderBottom: `1px solid ${THEME.border.primary}`,
                                        }}
                                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = THEME.bg.tertiary)}
                                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                                    >
                                        <span style={{ fontWeight: 600 }}>{symbol.replace('USDT', '')}</span>
                                        <span style={{ color: THEME.text.tertiary }}> / USDT</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <p style={{ fontSize: '11px', color: THEME.text.tertiary, margin: '4px 0 12px 0' }}>
                        Bật/tắt token để nhận hoặc bỏ qua tín hiệu. Token default không thể xóa.
                    </p>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
                        gap: '10px'
                    }}>
                        {tokenWatchlist.map((token) => {
                            const isDefault = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'TAOUSDT', 'FETUSDT', 'ONDOUSDT'].includes(token.symbol);
                            return (
                                <div
                                    key={token.symbol}
                                    style={{
                                        padding: '12px',
                                        borderRadius: '8px',
                                        backgroundColor: token.enabled ? 'rgba(14,203,129,0.1)' : THEME.bg.vessel,
                                        border: `1px solid ${token.enabled ? THEME.status.buy : THEME.border.primary}`,
                                        textAlign: 'center',
                                        position: 'relative',
                                    }}
                                >
                                    {/* Delete button for custom tokens */}
                                    {!isDefault && (
                                        <button
                                            onClick={() => handleRemoveToken(token.symbol)}
                                            style={{
                                                position: 'absolute',
                                                top: '4px',
                                                right: '4px',
                                                width: '18px',
                                                height: '18px',
                                                borderRadius: '50%',
                                                border: 'none',
                                                backgroundColor: THEME.status.sell,
                                                color: '#fff',
                                                fontSize: '10px',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                            }}
                                        >
                                            ×
                                        </button>
                                    )}
                                    <div
                                        onClick={() => handleTokenToggle(token.symbol)}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        <div style={{
                                            fontSize: '13px',
                                            fontWeight: 700,
                                            color: token.enabled ? THEME.text.primary : THEME.text.tertiary
                                        }}>
                                            {token.symbol.replace('USDT', '')}
                                        </div>
                                        <div style={{
                                            fontSize: '10px',
                                            color: THEME.text.tertiary,
                                            marginTop: '2px'
                                        }}>
                                            {token.alias || token.symbol}
                                        </div>
                                        <div style={{
                                            marginTop: '8px',
                                            width: '32px',
                                            height: '18px',
                                            borderRadius: '9px',
                                            backgroundColor: token.enabled ? THEME.status.buy : THEME.bg.tertiary,
                                            margin: '8px auto 0',
                                            position: 'relative',
                                            transition: 'background-color 0.2s',
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                top: '2px',
                                                left: token.enabled ? '16px' : '2px',
                                                width: '14px',
                                                height: '14px',
                                                borderRadius: '50%',
                                                backgroundColor: '#fff',
                                                transition: 'left 0.2s',
                                            }} />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Tab Content: Risk Management */}
            {activeTab === 'risk' && (
                <>
                    {/* Divider */}
                    <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: `1px solid ${THEME.border.primary}` }} />

                    {/* Risk Management */}
                    <div style={sectionStyle}>
                        <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>Quản lý rủi ro</h3>

                        <div style={gridStyle}>
                            <div>
                                <label style={labelStyle}>Rủi ro mỗi lệnh (%)</label>
                                <input
                                    type="number"
                                    min="0.1"
                                    max="10"
                                    step="0.1"
                                    value={settings.risk_percent}
                                    onChange={(e) => setSettings(s => ({ ...s, risk_percent: parseFloat(e.target.value) || 0 }))}
                                    style={{ ...inputStyle, borderColor: THEME.status.info }}
                                />
                            </div>
                            <div>
                                <label style={labelStyle}>Tỷ lệ R:R</label>
                                <input
                                    type="number"
                                    min="0.5"
                                    max="10"
                                    step="0.1"
                                    value={settings.rr_ratio}
                                    onChange={(e) => setSettings(s => ({ ...s, rr_ratio: parseFloat(e.target.value) || 0 }))}
                                    style={{ ...inputStyle, borderColor: THEME.status.info }}
                                />
                            </div>
                        </div>

                        <div style={gridStyle}>
                            <div>
                                <label style={labelStyle}>Số vị thế tối đa</label>
                                <input
                                    type="number"
                                    min="1"
                                    max="10"
                                    value={settings.max_positions}
                                    onChange={(e) => setSettings(s => ({ ...s, max_positions: parseInt(e.target.value) || 1 }))}
                                    style={inputStyle}
                                />
                            </div>
                            <div>
                                <label style={labelStyle}>Đòn bẩy</label>
                                <select
                                    value={settings.leverage}
                                    onChange={(e) => setSettings(s => ({ ...s, leverage: parseInt(e.target.value) }))}
                                    style={inputStyle}
                                >
                                    <option value={1}>1x</option>
                                    <option value={2}>2x</option>
                                    <option value={3}>3x</option>
                                    <option value={5}>5x</option>
                                    <option value={10}>10x</option>
                                </select>
                            </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <input
                                type="checkbox"
                                id="autoExecute"
                                checked={settings.auto_execute}
                                onChange={(e) => setSettings(s => ({ ...s, auto_execute: e.target.checked }))}
                                style={{ width: '16px', height: '16px', accentColor: THEME.accent.yellow }}
                            />
                            <label htmlFor="autoExecute" style={{ fontSize: '14px', color: THEME.text.secondary }}>
                                Tự động thực hiện tín hiệu
                            </label>
                        </div>
                    </div>

                    {/* Strategy Parameters */}
                    <div style={{ ...sectionStyle, marginTop: '16px', paddingTop: '16px', borderTop: `1px solid ${THEME.border.primary}` }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>Tham số chiến lược</h3>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                            <div style={cardStyle}>
                                <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>VWAP</div>
                                <div style={{ fontFamily: 'monospace', color: THEME.accent.yellow }}>Period: 14</div>
                            </div>
                            <div style={cardStyle}>
                                <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>Bollinger Bands</div>
                                <div style={{ fontFamily: 'monospace', color: THEME.status.info }}>20, 2σ</div>
                            </div>
                            <div style={cardStyle}>
                                <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>StochRSI</div>
                                <div style={{ fontFamily: 'monospace', color: THEME.status.purple }}>14, 3, 3</div>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginTop: '16px',
                        paddingTop: '16px',
                        borderTop: `1px solid ${THEME.border.primary}`
                    }}>
                        <button
                            onClick={handleReset}
                            style={{
                                ...buttonStyle(THEME.alpha.sellBg, THEME.status.sell),
                                border: `1px solid ${THEME.status.sell}`,
                            }}
                        >
                            Reset tài khoản
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={isSaving}
                            style={{
                                ...buttonStyle(THEME.accent.yellow, '#000'),
                                opacity: isSaving ? 0.5 : 1,
                            }}
                        >
                            {isSaving ? 'Đang lưu...' : 'Lưu cài đặt'}
                        </button>
                    </div>
                </>
            )}

            {/* Tab Content: Strategy */}
            {activeTab === 'strategy' && (
                <div style={sectionStyle}>
                    <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>Tham số chiến lược</h3>
                    <p style={{ fontSize: '11px', color: THEME.text.tertiary, margin: '4px 0 12px 0' }}>
                        Các tham số kỹ thuật cho signal generation
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>VWAP</div>
                            <div style={{ fontFamily: 'monospace', color: THEME.accent.yellow }}>Period: 14</div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>Bollinger Bands</div>
                            <div style={{ fontFamily: 'monospace', color: THEME.status.info }}>20, 2σ</div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '12px', color: THEME.text.tertiary }}>StochRSI</div>
                            <div style={{ fontFamily: 'monospace', color: THEME.status.purple }}>14, 3, 3</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tab Content: Debug */}
            {activeTab === 'debug' && (
                <div style={sectionStyle}>
                    <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" />
                        </svg>
                        Debug / Test
                    </h3>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                        <button
                            onClick={() => handleSimulateSignal('BUY')}
                            disabled={isSimulating}
                            style={{
                                ...buttonStyle(THEME.status.buy, '#fff'),
                                flex: 1,
                                opacity: isSimulating ? 0.5 : 1,
                            }}
                        >
                            {isSimulating ? '...' : '▲ Test BUY'}
                        </button>
                        <button
                            onClick={() => handleSimulateSignal('SELL')}
                            disabled={isSimulating}
                            style={{
                                ...buttonStyle(THEME.status.sell, '#fff'),
                                flex: 1,
                                opacity: isSimulating ? 0.5 : 1,
                            }}
                        >
                            {isSimulating ? '...' : '▼ Test SELL'}
                        </button>
                    </div>
                    <p style={{ fontSize: '12px', color: THEME.text.tertiary, margin: '8px 0 0 0' }}>
                        Giả lập tín hiệu để test luồng đặt lệnh → Database → Hiển thị
                    </p>

                    <div style={{ marginTop: '16px' }}>
                        <button
                            onClick={handleReset}
                            style={{
                                ...buttonStyle(THEME.alpha.sellBg, THEME.status.sell),
                                border: `1px solid ${THEME.status.sell}`,
                            }}
                        >
                            Reset tài khoản
                        </button>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div style={{
                    marginTop: '16px',
                    padding: '8px',
                    borderRadius: '4px',
                    backgroundColor: THEME.alpha.sellBg,
                    color: THEME.status.sell,
                    fontSize: '12px'
                }}>
                    {error}
                </div>
            )}
        </div>
    );
};

export default Settings;

