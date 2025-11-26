import { useEffect, useState } from 'react';
import './App.css';
import { useMarketData } from './hooks/useMarketData';
import CandleChart from './components/CandleChart';
import Portfolio from './components/Portfolio';
import TradeHistory from './components/TradeHistory';
import PerformanceDashboard from './components/PerformanceDashboard';
import Settings from './components/Settings';
import StrategyMonitor from './components/StrategyMonitor';
import SignalLogItem from './components/SignalLogItem';

interface SystemStatus {
  status: string;
  timestamp: string;
  service: string;
  version: string;
}

interface SignalLog {
  id: number;
  time: string;
  action: string;
  adx: number;
  trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
}

type Tab = 'chart' | 'portfolio' | 'history' | 'performance' | 'settings';
type BottomTab = 'positions' | 'orders' | 'history';

// Design tokens - inline styles guarantee rendering
const C = {
  up: '#0ECB81',
  down: '#F6465D',
  yellow: '#F0B90B',
  bg: '#0B0E11',
  card: '#1E2329',
  sidebar: '#09090b',
  border: '#2B3139',
  text1: '#EAECEF',
  text2: '#848E9C',
  text3: '#5E6673',
};

function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('chart');
  const [bottomTab, setBottomTab] = useState<BottomTab>('positions');
  const [isBottomPanelHidden, setIsBottomPanelHidden] = useState(false);
  const { data: marketData, isConnected, reconnectState, reconnectNow } = useMarketData('btcusdt');
  const [signalLogs, setSignalLogs] = useState<SignalLog[]>([
    { id: 1, time: '18:40:05', action: 'INIT', adx: 0, trend: 'NEUTRAL' },
    { id: 2, time: '18:40:06', action: 'CONN', adx: 0, trend: 'NEUTRAL' },
    { id: 3, time: '18:40:10', action: 'SCAN', adx: 32, trend: 'BULLISH' },
  ]);

  // Keyboard shortcut for fullscreen toggle
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && activeTab === 'chart') {
        setIsBottomPanelHidden(prev => !prev);
      }
      // F key for fullscreen
      if (e.key === 'f' && activeTab === 'chart' && !e.ctrlKey && !e.metaKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          setIsBottomPanelHidden(prev => !prev);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab]);

  // Trigger resize when bottom panel is toggled so chart can resize
  useEffect(() => {
    // Small delay to allow DOM to update first
    const timer = setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 50);
    return () => clearTimeout(timer);
  }, [isBottomPanelHidden]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/system/status');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setStatus(data);
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString('vi-VN', { 
          hour: '2-digit', minute: '2-digit', second: '2-digit',
          timeZone: 'Asia/Ho_Chi_Minh'
        });
        
        const adx = Math.floor(Math.random() * 30) + 20;
        const trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL' = marketData && marketData.vwap 
          ? (marketData.close > marketData.vwap ? 'BULLISH' : 'BEARISH') 
          : 'NEUTRAL';
        setSignalLogs(prev => {
          const newId = Date.now() + Math.random();
          return [...prev.slice(-49), { id: newId, time: timeStr, action: 'SCAN', adx, trend }];
        });
      } catch (err) {
        console.error("Failed to fetch status:", err);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, [marketData]);

  const tabs: { id: Tab; label: string }[] = [
    { id: 'chart', label: 'Chart' },
    { id: 'portfolio', label: 'Portfolio' },
    { id: 'history', label: 'History' },
    { id: 'settings', label: 'Settings' },
  ];

  const formatPrice = (price: number) => price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const trendBias = marketData && marketData.vwap 
    ? (marketData.close > marketData.vwap ? 'LONG' : 'SHORT') 
    : 'NEUTRAL';
  const adxValue = 32;
  const isLive = status?.status === 'ok';
  const priceColor = marketData?.change_percent && marketData.change_percent >= 0 ? C.up : C.down;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      overflow: 'hidden',
      userSelect: 'none',
      backgroundColor: C.bg,
      color: C.text1,
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>
      
      {/* HEADER */}
      <header style={{
        height: '48px',
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        backgroundColor: C.card,
        borderBottom: `1px solid ${C.border}`,
      }}>
        {/* Left: Logo + Nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 700, fontSize: '20px', letterSpacing: '-0.05em', color: C.yellow }}>Hinto</span>
            <span style={{
              fontSize: '10px',
              textTransform: 'uppercase',
              fontWeight: 700,
              letterSpacing: '0.1em',
              padding: '2px 6px',
              borderRadius: '4px',
              border: `1px solid ${C.border}`,
              color: C.text2,
            }}>Pro</span>
          </div>

          {/* Navigation */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '6px 12px',
                  fontSize: '14px',
                  fontWeight: 500,
                  borderRadius: '6px',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  backgroundColor: activeTab === tab.id ? C.border : 'transparent',
                  color: activeTab === tab.id ? C.yellow : C.text2,
                }}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        
        {/* Right: Balance + Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: 700, color: C.text3 }}>Virtual Balance</div>
            <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: C.up }}>$10,000.00</div>
          </div>
          <div style={{ height: '32px', width: '1px', backgroundColor: C.border }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isLive ? C.up : C.down,
              boxShadow: isLive ? `0 0 8px ${C.up}` : 'none',
            }} />
            <span style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.05em', color: isLive ? C.up : C.down }}>
              {isLive ? 'LIVE' : 'OFF'}
            </span>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT - Fixed height calculation */}
      <main style={{ 
        height: 'calc(100vh - 48px)', 
        minHeight: 0, 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {activeTab === 'chart' ? (
          <>
            {/* TICKER BAR */}
            <div style={{
              height: '40px',
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              padding: '0 16px',
              gap: '24px',
              fontSize: '14px',
              backgroundColor: C.card,
              borderBottom: `1px solid ${C.border}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontWeight: 700, color: C.text1 }}>BTC/USDT</span>
                <span style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontWeight: 500,
                  backgroundColor: 'rgba(240,185,11,0.15)',
                  color: C.yellow,
                }}>15m</span>
              </div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '18px', fontWeight: 700, color: priceColor }}>
                ${marketData ? formatPrice(marketData.close) : '---'}
              </div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '14px', color: priceColor }}>
                {marketData?.change_percent !== undefined ? `${marketData.change_percent >= 0 ? '+' : ''}${marketData.change_percent.toFixed(2)}%` : '---'}
              </div>
              <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: C.text2 }}>
                <span>H: <span style={{ fontFamily: "'JetBrains Mono', monospace", color: C.text1 }}>{marketData?.high ? formatPrice(marketData.high) : '---'}</span></span>
                <span>L: <span style={{ fontFamily: "'JetBrains Mono', monospace", color: C.text1 }}>{marketData?.low ? formatPrice(marketData.low) : '---'}</span></span>
                <span>RSI: <span style={{ fontFamily: "'JetBrains Mono', monospace", color: (marketData?.rsi || 50) > 70 ? C.down : (marketData?.rsi || 50) < 30 ? C.up : C.text1 }}>{marketData?.rsi?.toFixed(1) || '---'}</span></span>
                <span>VWAP: <span style={{ fontFamily: "'JetBrains Mono', monospace", color: C.yellow }}>{marketData?.vwap ? formatPrice(marketData.vwap) : '---'}</span></span>
              </div>
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Fullscreen Toggle Button */}
                <button
                  onClick={() => setIsBottomPanelHidden(!isBottomPanelHidden)}
                  title={isBottomPanelHidden ? 'Show Panel (Esc)' : 'Fullscreen Chart'}
                  style={{
                    padding: '4px 8px',
                    fontSize: '11px',
                    fontWeight: 500,
                    borderRadius: '4px',
                    border: `1px solid ${C.border}`,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    backgroundColor: isBottomPanelHidden ? C.yellow : 'transparent',
                    color: isBottomPanelHidden ? '#000' : C.text2,
                    transition: 'all 0.2s',
                  }}
                >
                  {isBottomPanelHidden ? '⊟' : '⊞'} {isBottomPanelHidden ? 'Exit' : 'Full'}
                </button>
                
                {/* Connection Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <div style={{ 
                    width: '6px', 
                    height: '6px', 
                    borderRadius: '50%', 
                    backgroundColor: isConnected ? C.up : (reconnectState.isReconnecting ? C.yellow : C.down),
                    animation: reconnectState.isReconnecting ? 'pulse 1s infinite' : 'none'
                  }} />
                  <span style={{ 
                    fontSize: '12px', 
                    fontWeight: 500,
                    color: isConnected ? C.up : (reconnectState.isReconnecting ? C.yellow : C.down)
                  }}>
                    {isConnected ? 'LIVE' : (reconnectState.isReconnecting ? `Reconnecting ${reconnectState.nextRetryIn}s...` : 'DISCONNECTED')}
                  </span>
                  {!isConnected && (
                    <button
                      onClick={reconnectNow}
                      style={{
                        marginLeft: '8px',
                        padding: '2px 8px',
                        fontSize: '10px',
                        fontWeight: 600,
                        color: '#000',
                        backgroundColor: C.yellow,
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                    >
                      Reconnect
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Trading View Layout - calc height minus ticker bar */}
            <div style={{ flex: 1, minHeight: 0, display: 'flex', overflow: 'hidden' }}>
              
              {/* LEFT: Chart + Bottom Panel */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, minWidth: 0, borderRight: `1px solid ${C.border}`, overflow: 'hidden' }}>
                <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
                  <CandleChart />
                </div>

                {/* Bottom Panel - Collapsible */}
                {!isBottomPanelHidden && (
                  <div style={{ height: '176px', flexShrink: 0, display: 'flex', flexDirection: 'column', backgroundColor: C.card, borderTop: `1px solid ${C.border}` }}>
                    <div style={{ display: 'flex', borderBottom: `1px solid ${C.border}` }}>
                      {(['positions', 'orders', 'history'] as BottomTab[]).map((tab) => (
                        <button
                          key={tab}
                          onClick={() => setBottomTab(tab)}
                          style={{
                            padding: '8px 16px',
                            fontSize: '12px',
                            fontWeight: 500,
                            border: 'none',
                            cursor: 'pointer',
                            borderBottom: bottomTab === tab ? `2px solid ${C.yellow}` : '2px solid transparent',
                            color: bottomTab === tab ? C.text1 : C.text2,
                            backgroundColor: bottomTab === tab ? C.border : 'transparent',
                          }}
                        >
                          {tab === 'positions' && 'Positions (0)'}
                          {tab === 'orders' && 'Open Orders (0)'}
                          {tab === 'history' && 'Trade History'}
                        </button>
                      ))}
                    </div>
                    <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
                      <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ color: C.text2, textAlign: 'left' }}>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>Symbol</th>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>Size</th>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>Entry</th>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>Mark</th>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>PnL</th>
                            <th style={{ paddingBottom: '8px', fontWeight: 500 }}>ROE%</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr><td colSpan={6} style={{ padding: '16px 0', textAlign: 'center', color: C.text3 }}>No open positions</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>

              {/* RIGHT SIDEBAR */}
              <aside style={{ width: '320px', flexShrink: 0, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden', backgroundColor: C.sidebar, borderLeft: `1px solid ${C.border}` }}>
                
                <StrategyMonitor trendBias={trendBias} adxValue={adxValue} stochRsiValue={marketData?.rsi || 50} />

                {/* Signal Logs */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
                  <div style={{
                    padding: '8px 12px',
                    fontSize: '10px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexShrink: 0,
                    backgroundColor: C.sidebar,
                    borderBottom: `1px solid ${C.border}`,
                    color: C.text3,
                  }}>
                    <span>Live Feed</span>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '9px', padding: '2px 6px', borderRadius: '4px', backgroundColor: C.border }}>
                      {signalLogs.length}
                    </span>
                  </div>
                  
                  <div style={{ flex: 1, overflowY: 'auto', padding: '4px 12px', fontFamily: "'JetBrains Mono', monospace" }}>
                    {signalLogs.slice(-30).map((log) => (
                      <SignalLogItem key={log.id} time={log.time} action={log.action} adx={log.adx} trend={log.trend} />
                    ))}
                  </div>
                </div>

                {/* Mode Badge */}
                <div style={{
                  flexShrink: 0,
                  padding: '8px 12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '10px',
                  borderTop: `1px solid ${C.border}`,
                  backgroundColor: C.sidebar,
                }}>
                  <span style={{ color: C.text3 }}>Mode</span>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontWeight: 700,
                    letterSpacing: '0.05em',
                    backgroundColor: 'rgba(240,185,11,0.15)',
                    color: C.yellow,
                  }}>PAPER</span>
                </div>
              </aside>
            </div>
          </>
        ) : (
          <div style={{ height: '100%', overflowY: 'auto', padding: '16px' }}>
            <div style={{ maxWidth: '1152px', margin: '0 auto' }}>
              {activeTab === 'portfolio' && <Portfolio />}
              {activeTab === 'history' && <TradeHistory />}
              {activeTab === 'performance' && <PerformanceDashboard />}
              {activeTab === 'settings' && <Settings />}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
