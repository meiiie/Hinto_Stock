import React from 'react';
import { Play, Square, Shield, Skull } from 'lucide-react';

interface ControlPanelProps {
  mode: string;
  totalEquity: number;
  dailyPnL: number;
  onToggleMode: () => void;
  isRunning: boolean;
  onToggleRun: () => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({ 
  mode, totalEquity, dailyPnL, onToggleMode, isRunning, onToggleRun 
}) => {
  const isAggressive = mode === 'AGGRESSIVE';

  return (
    <div className="h-full bg-gray-900 border-l border-gray-800 p-4 flex flex-col w-72">
      {/* Account Status */}
      <div className="bg-gray-800 rounded-lg p-4 mb-4 border border-gray-700">
        <div className="text-gray-400 text-xs mb-1">Total Equity</div>
        <div className="text-3xl font-bold text-white mb-2">${totalEquity.toLocaleString()}</div>
        <div className="flex justify-between items-end">
          <div className="text-gray-400 text-xs">Daily PnL</div>
          <div className={`font-mono ${dailyPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {dailyPnL >= 0 ? '+' : ''}${dailyPnL.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="mb-6">
        <div className="text-xs text-gray-500 mb-2 uppercase font-bold tracking-wider">Strategy Mode</div>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => isAggressive && onToggleMode()}
            className={`p-3 rounded-lg flex flex-col items-center gap-1 border transition-all ${
              !isAggressive 
                ? 'bg-green-900/20 border-green-500 text-green-400 ring-1 ring-green-500/50' 
                : 'bg-gray-800 border-gray-700 text-gray-500 hover:bg-gray-700'
            }`}
          >
            <Shield className="w-5 h-5" />
            <span className="text-xs font-bold">SAFE</span>
          </button>
          <button
            onClick={() => !isAggressive && onToggleMode()}
            className={`p-3 rounded-lg flex flex-col items-center gap-1 border transition-all ${
              isAggressive 
                ? 'bg-red-900/20 border-red-500 text-red-400 ring-1 ring-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]' 
                : 'bg-gray-800 border-gray-700 text-gray-500 hover:bg-gray-700'
            }`}
          >
            <Skull className="w-5 h-5" />
            <span className="text-xs font-bold">BEAST</span>
          </button>
        </div>
        <div className="mt-2 text-[10px] text-gray-400 px-1">
          {isAggressive 
            ? "⚠️ 10x Leverage. No Circuit Breaker. High Risk." 
            : "🛡️ 5x Leverage. 12h Cooldown on loss."}
        </div>
      </div>

      {/* Settings */}
      <div className="space-y-3 mb-6 flex-1">
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Risk per Trade</label>
          <div className="relative">
            <input 
              type="number" 
              value={isAggressive ? 5 : 2} 
              disabled 
              className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white text-right pr-8"
            />
            <span className="absolute right-3 top-2 text-gray-400">%</span>
          </div>
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Max Leverage</label>
          <div className="relative">
            <input 
              type="number" 
              value={isAggressive ? 10 : 5} 
              disabled 
              className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white text-right pr-8"
            />
            <span className="absolute right-3 top-2 text-gray-400">x</span>
          </div>
        </div>
      </div>

      {/* Master Button */}
      <button
        onClick={onToggleRun}
        className={`w-full py-4 rounded-lg font-bold text-lg flex items-center justify-center gap-2 transition-all ${
          isRunning 
            ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/30' 
            : 'bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/30'
        }`}
      >
        {isRunning ? (
          <>
            <Square className="fill-current" /> STOP ENGINE
          </>
        ) : (
          <>
            <Play className="fill-current" /> START ENGINE
          </>
        )}
      </button>
    </div>
  );
};
