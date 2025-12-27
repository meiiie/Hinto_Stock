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

/**
 * Settings Component - Binance Style with Inline Styles
 * Fixed for Tailwind v4 compatibility
 */
const Settings: React.FC = () => {
    const [settings, setSettings] = useState<TradingSettings>({
        risk_percent: 1.5,
        rr_ratio: 1.5,
        max_positions: 3,
        leverage: 1,
        auto_execute: false
    });
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
        } catch (err) {
            setError('Không thể tải cài đặt');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

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
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: THEME.text.primary, margin: 0 }}>Cài đặt</h2>
                {saveSuccess && (
                    <span style={{ fontSize: '12px', color: THEME.status.buy }}>✓ Đã lưu</span>
                )}
            </div>

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

            {/* Debug/Test Actions */}
            <div style={{ ...sectionStyle, marginTop: '16px', paddingTop: '16px', borderTop: `1px solid ${THEME.border.primary}` }}>
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: THEME.text.secondary, margin: 0 }}>
                    🔧 Debug / Test
                </h3>
                <div style={{ display: 'flex', gap: '8px' }}>
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
                <p style={{ fontSize: '12px', color: THEME.text.tertiary, margin: 0 }}>
                    Giả lập tín hiệu để test luồng đặt lệnh → Database → Hiển thị
                </p>
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
        </div>
    );
};

export default Settings;
