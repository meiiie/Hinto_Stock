import React, { useState, useEffect } from 'react';
import { THEME } from '../styles/theme';

interface SystemStatus {
    status: string;
    service: string;
    version: string;
    uptime?: number;
    connections?: number;
}

interface ConnectionStatusProps {
    isConnected: boolean;
    error?: string | null;
}

/**
 * Connection Status Component - Binance Style
 * Shows Online/Offline indicator and service info
 */
const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ isConnected, error }) => {
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
    const [isReconnecting, setIsReconnecting] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/system/status');
                if (response.ok) {
                    const data = await response.json();
                    setSystemStatus(data);
                }
            } catch (err) {
                console.error('Failed to fetch system status:', err);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        setIsReconnecting(!isConnected && !error);
    }, [isConnected, error]);

    const getStatusConfig = () => {
        if (isConnected) return { color: THEME.status.buy, bg: THEME.alpha.buyBg, text: 'Trực tuyến' };
        if (isReconnecting) return { color: THEME.accent.yellow, bg: THEME.alpha.warningBg, text: 'Đang kết nối...' };
        return { color: THEME.status.sell, bg: THEME.alpha.sellBg, text: 'Mất kết nối' };
    };

    const status = getStatusConfig();

    return (
        <div className="flex items-center gap-3 rounded-lg px-3 py-2" style={{ backgroundColor: THEME.bg.secondary }}>
            {/* Status Indicator */}
            <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isReconnecting ? 'animate-pulse' : ''}`} style={{ backgroundColor: status.color }} />
                <span className="text-xs font-medium" style={{ color: status.color }}>
                    {status.text}
                </span>
            </div>

            {/* Divider */}
            <div className="w-px h-4" style={{ backgroundColor: THEME.border.primary }} />

            {/* Service Info */}
            {systemStatus && (
                <div className="flex items-center gap-2 text-xs" style={{ color: THEME.text.tertiary }}>
                    <span className="font-semibold" style={{ color: THEME.text.secondary }}>{systemStatus.service}</span>
                    <span>v{systemStatus.version}</span>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <>
                    <div className="w-px h-4" style={{ backgroundColor: THEME.border.primary }} />
                    <span className="text-xs" style={{ color: THEME.status.sell }}>{error}</span>
                </>
            )}
        </div>
    );
};

export default ConnectionStatus;
