import React, { useState, useEffect, useCallback } from 'react';
import { THEME } from '../styles/theme';

interface TradingSettings {
    risk_percent: number;
    rr_ratio: number;
    max_positions: number;
    leverage: number;
    auto_execute: boolean;
}

/**
 * Settings Component - Binance Style
 * Allows editing Risk %, R:R ratio, and displays strategy parameters
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

    const fetchSettings = useCallback(async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/settings');
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
            const response = await fetch('http://127.0.0.1:8000/settings', {
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
            const response = await fetch('http://127.0.0.1:8000/trades/reset', { method: 'POST' });
            if (response.ok) {
                alert('Đã reset tài khoản thành công!');
            }
        } catch (err) {
            setError('Không thể reset tài khoản');
        }
    };

    const inputStyle = {
        backgroundColor: THEME.bg.vessel,
        border: `1px solid ${THEME.border.input}`,
        color: THEME.text.primary,
    };

    if (isLoading) {
        return (
            <div className="rounded-lg p-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
                <div className="animate-pulse space-y-4">
                    <div className="h-4 rounded w-1/3" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="h-10 rounded" style={{ backgroundColor: THEME.bg.vessel }}></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="rounded-lg p-4 space-y-4" style={{ backgroundColor: THEME.bg.secondary, border: `1px solid ${THEME.border.primary}` }}>
            {/* Header */}
            <div className="flex justify-between items-center pb-3" style={{ borderBottom: `1px solid ${THEME.border.primary}` }}>
                <h2 className="text-lg font-bold" style={{ color: THEME.text.primary }}>Cài đặt</h2>
                {saveSuccess && (
                    <span className="text-xs animate-pulse" style={{ color: THEME.status.buy }}>✓ Đã lưu</span>
                )}
            </div>

            {/* Risk Management */}
            <div className="space-y-3">
                <h3 className="text-sm font-semibold" style={{ color: THEME.text.secondary }}>Quản lý rủi ro</h3>
                
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs mb-1" style={{ color: THEME.text.tertiary }}>Rủi ro mỗi lệnh (%)</label>
                        <input
                            type="number"
                            min="0.1"
                            max="10"
                            step="0.1"
                            value={settings.risk_percent}
                            onChange={(e) => setSettings(s => ({ ...s, risk_percent: parseFloat(e.target.value) || 0 }))}
                            className="w-full rounded px-3 py-2 text-sm focus:outline-none"
                            style={{ ...inputStyle, borderColor: THEME.status.info }}
                        />
                    </div>
                    <div>
                        <label className="block text-xs mb-1" style={{ color: THEME.text.tertiary }}>Tỷ lệ R:R</label>
                        <input
                            type="number"
                            min="0.5"
                            max="10"
                            step="0.1"
                            value={settings.rr_ratio}
                            onChange={(e) => setSettings(s => ({ ...s, rr_ratio: parseFloat(e.target.value) || 0 }))}
                            className="w-full rounded px-3 py-2 text-sm focus:outline-none"
                            style={{ ...inputStyle, borderColor: THEME.status.info }}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs mb-1" style={{ color: THEME.text.tertiary }}>Số vị thế tối đa</label>
                        <input
                            type="number"
                            min="1"
                            max="10"
                            value={settings.max_positions}
                            onChange={(e) => setSettings(s => ({ ...s, max_positions: parseInt(e.target.value) || 1 }))}
                            className="w-full rounded px-3 py-2 text-sm focus:outline-none"
                            style={inputStyle}
                        />
                    </div>
                    <div>
                        <label className="block text-xs mb-1" style={{ color: THEME.text.tertiary }}>Đòn bẩy</label>
                        <select
                            value={settings.leverage}
                            onChange={(e) => setSettings(s => ({ ...s, leverage: parseInt(e.target.value) }))}
                            className="w-full rounded px-3 py-2 text-sm focus:outline-none"
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

                <div className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        id="autoExecute"
                        checked={settings.auto_execute}
                        onChange={(e) => setSettings(s => ({ ...s, auto_execute: e.target.checked }))}
                        className="w-4 h-4 rounded"
                        style={{ accentColor: THEME.accent.yellow }}
                    />
                    <label htmlFor="autoExecute" className="text-sm" style={{ color: THEME.text.secondary }}>
                        Tự động thực hiện tín hiệu
                    </label>
                </div>
            </div>

            {/* Strategy Parameters (Read-only) */}
            <div className="space-y-3 pt-3" style={{ borderTop: `1px solid ${THEME.border.primary}` }}>
                <h3 className="text-sm font-semibold" style={{ color: THEME.text.secondary }}>Tham số chiến lược</h3>
                
                <div className="grid grid-cols-3 gap-3 text-xs">
                    <div className="rounded p-2" style={{ backgroundColor: THEME.bg.vessel }}>
                        <div style={{ color: THEME.text.tertiary }}>VWAP</div>
                        <div className="font-mono" style={{ color: THEME.accent.yellow }}>Period: 14</div>
                    </div>
                    <div className="rounded p-2" style={{ backgroundColor: THEME.bg.vessel }}>
                        <div style={{ color: THEME.text.tertiary }}>Bollinger Bands</div>
                        <div className="font-mono" style={{ color: THEME.status.info }}>20, 2σ</div>
                    </div>
                    <div className="rounded p-2" style={{ backgroundColor: THEME.bg.vessel }}>
                        <div style={{ color: THEME.text.tertiary }}>StochRSI</div>
                        <div className="font-mono" style={{ color: THEME.status.purple }}>14, 3, 3</div>
                    </div>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="text-xs rounded p-2" style={{ backgroundColor: THEME.alpha.sellBg, color: THEME.status.sell }}>
                    {error}
                </div>
            )}

            {/* Actions */}
            <div className="flex justify-between pt-3" style={{ borderTop: `1px solid ${THEME.border.primary}` }}>
                <button
                    onClick={handleReset}
                    className="px-4 py-2 text-xs rounded transition-colors hover:opacity-80"
                    style={{ backgroundColor: THEME.alpha.sellBg, color: THEME.status.sell, border: `1px solid ${THEME.status.sell}` }}
                >
                    Reset tài khoản
                </button>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="px-4 py-2 text-xs rounded transition-colors hover:opacity-80 disabled:opacity-50"
                    style={{ backgroundColor: THEME.accent.yellow, color: '#000' }}
                >
                    {isSaving ? 'Đang lưu...' : 'Lưu cài đặt'}
                </button>
            </div>
        </div>
    );
};

export default Settings;
