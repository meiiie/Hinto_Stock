import React from 'react';
import { useMarketData } from '../hooks/useMarketData';

const PriceTicker: React.FC = () => {
    const { data, isConnected } = useMarketData('btcusdt');

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    };

    return (
        <div className="bg-zinc-950/90 backdrop-blur-sm border border-zinc-800 rounded-lg p-3 min-w-[200px]">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">BTC/USDT</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-medium">
                        Perp
                    </span>
                </div>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
            </div>

            {data ? (
                <>
                    {/* Price */}
                    <div className="text-2xl font-bold font-mono text-white tracking-tight">
                        ${formatPrice(data.close)}
                    </div>
                    
                    {/* Change */}
                    {data.change_percent !== undefined && (
                        <div className={`text-sm font-mono font-medium ${
                            data.change_percent >= 0 ? 'text-emerald-400' : 'text-rose-400'
                        }`}>
                            {data.change_percent >= 0 ? '+' : ''}{data.change_percent.toFixed(2)}%
                        </div>
                    )}

                    {/* Indicators Row */}
                    <div className="flex gap-3 mt-2 pt-2 border-t border-zinc-800">
                        <div>
                            <div className="text-[10px] text-zinc-500 uppercase">RSI</div>
                            <div className={`text-xs font-mono font-medium ${
                                (data.rsi || 0) > 70 ? 'text-rose-400' : 
                                (data.rsi || 0) < 30 ? 'text-emerald-400' : 'text-zinc-300'
                            }`}>
                                {data.rsi?.toFixed(1) || '-'}
                            </div>
                        </div>
                        <div>
                            <div className="text-[10px] text-zinc-500 uppercase">VWAP</div>
                            <div className="text-xs font-mono font-medium text-yellow-500">
                                {data.vwap ? formatPrice(data.vwap) : '-'}
                            </div>
                        </div>
                    </div>

                    {/* Signal */}
                    {data.signal && data.signal.type !== 'hold' && (
                        <div className={`mt-2 px-2 py-1 rounded text-xs font-bold text-center ${
                            data.signal.type === 'buy' 
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                                : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        }`}>
                            {data.signal.type === 'buy' ? '🔼 BUY SIGNAL' : '🔽 SELL SIGNAL'}
                        </div>
                    )}
                </>
            ) : (
                <div className="text-zinc-500 text-sm animate-pulse">Connecting...</div>
            )}
        </div>
    );
};

export default PriceTicker;
