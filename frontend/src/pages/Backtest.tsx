import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BacktestResult {
  symbol: string;
  equity: { timestamp: number; balance: number }[];
  stats: {
    total_trades: number;
    win_rate: number;
    net_return_pct: number;
    profit_factor: number;
    max_drawdown: number;
  };
  trades: any[];
}

const Backtest: React.FC = () => {
  const [params, setParams] = useState({
    symbol: 'BTCUSDT',
    interval: '15m',
    days: 7,
    balance: 10000
  });
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runBacktest = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/backtest/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6 flex items-center">
        🧪 Strategy Backtest
      </h1>

      {/* Control Panel */}
      <div className="bg-gray-800 p-4 rounded-lg shadow-lg mb-6 flex gap-4 items-end flex-wrap">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Symbol</label>
          <input 
            type="text" 
            value={params.symbol}
            onChange={e => setParams({...params, symbol: e.target.value.toUpperCase()})}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 w-32"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Interval</label>
          <select 
            value={params.interval}
            onChange={e => setParams({...params, interval: e.target.value})}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white w-24"
          >
            <option value="1m">1m</option>
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Days</label>
          <input 
            type="number" 
            value={params.days}
            onChange={e => setParams({...params, days: parseInt(e.target.value)})}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white w-24"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Balance ($)</label>
          <input 
            type="number" 
            value={params.balance}
            onChange={e => setParams({...params, balance: parseFloat(e.target.value)})}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white w-32"
          />
        </div>
        
        <button 
          onClick={runBacktest}
          disabled={loading}
          className={`px-6 py-2 rounded font-bold transition-colors ${
            loading 
              ? 'bg-gray-600 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-500'
          }`}
        >
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded mb-6">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <StatCard label="Total Trades" value={result.stats.total_trades} />
            <StatCard 
              label="Win Rate" 
              value={`${result.stats.win_rate.toFixed(1)}%`} 
              color={result.stats.win_rate > 50 ? 'text-green-400' : 'text-red-400'}
            />
            <StatCard 
              label="Net Return" 
              value={`${result.stats.net_return_pct.toFixed(2)}%`}
              color={result.stats.net_return_pct >= 0 ? 'text-green-400' : 'text-red-400'}
            />
            <StatCard label="Profit Factor" value={result.stats.profit_factor.toFixed(2)} />
            <StatCard label="Max Drawdown" value={`${(result.stats.max_drawdown * 100).toFixed(2)}%`} color="text-red-400" />
          </div>

          {/* Equity Chart */}
          <div className="bg-gray-800 p-4 rounded-lg shadow-lg h-96">
            <h3 className="text-xl font-bold mb-4 text-gray-300">Equity Curve</h3>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={result.equity}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(ts) => new Date(ts * 1000).toLocaleDateString()}
                  stroke="#9CA3AF"
                />
                <YAxis domain={['auto', 'auto']} stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', color: '#fff' }}
                  labelFormatter={(ts) => new Date(ts * 1000).toLocaleString()}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Balance']}
                />
                <Line 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#3B82F6" 
                  strokeWidth={2} 
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          {/* Trade List (Simple) */}
          {result.trades.length > 0 ? (
             <div className="bg-gray-800 p-4 rounded-lg">
                <h3 className="text-xl font-bold mb-4 text-gray-300">Trade History</h3>
                <div className="overflow-x-auto max-h-96 overflow-y-auto">
                    <table className="w-full text-left text-sm text-gray-400">
                        <thead className="bg-gray-700 text-gray-200 uppercase sticky top-0">
                            <tr>
                                <th className="px-4 py-2">Type</th>
                                <th className="px-4 py-2">Entry Time</th>
                                <th className="px-4 py-2">Entry</th>
                                <th className="px-4 py-2">Exit</th>
                                <th className="px-4 py-2">PnL</th>
                                <th className="px-4 py-2">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {result.trades.map((t, idx) => (
                                <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/50">
                                    <td className={`px-4 py-2 font-bold ${t.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>{t.direction}</td>
                                    <td className="px-4 py-2">{new Date(t.entry_time * 1000).toLocaleString()}</td>
                                    <td className="px-4 py-2">${t.entry_price.toFixed(2)}</td>
                                    <td className="px-4 py-2">{t.exit_price ? `$${t.exit_price.toFixed(2)}` : '-'}</td>
                                    <td className={`px-4 py-2 font-bold ${t.pnl > 0 ? 'text-green-400' : t.pnl < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                                        {t.pnl ? `$${t.pnl.toFixed(2)}` : '-'}
                                    </td>
                                    <td className="px-4 py-2">
                                        <span className={`px-2 py-1 rounded text-xs ${t.status === 'CLOSED' ? 'bg-gray-600' : 'bg-blue-900 text-blue-200'}`}>
                                            {t.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
             </div>
          ) : (
            <div className="text-center text-gray-500 py-8">No trades executed in this period.</div>
          )}
        </div>
      )}
    </div>
  );
};

const StatCard = ({ label, value, color = 'text-white' }: { label: string, value: string | number, color?: string }) => (
  <div className="bg-gray-800 p-4 rounded-lg shadow border-l-4 border-blue-600">
    <div className="text-gray-400 text-sm mb-1">{label}</div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
  </div>
);

export default Backtest;
