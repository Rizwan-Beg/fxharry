// /src/App.tsx
import React, { useState } from 'react';
import { TradingDashboard } from './components/TradingDashboard';
import { StrategiesPanel } from './components/StrategiesPanel';
import { RiskManagement } from './components/RiskManagement';
import { BacktestingPanel } from './components/BacktestingPanel';
import { ConnectionStatus } from './components/ConnectionStatus';
import { NotificationCenter } from './components/NotificationCenter';
import { useLiveFeed } from './hooks/useLiveFeed';
import { useMarketData } from './hooks/useMarketData';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  // NEW: Selected symbol for chart switching
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD');

  const { 
    marketData, 
    signals, 
    notifications, 
    connectionStatus,
    subscribeToSymbol,
    unsubscribeFromSymbol,
  } = useLiveFeed();
  
  const { 
    accountData, 
    positions, 
    riskAssessment 
  } = useMarketData();

  // If your useWebSocket exposes a subscribe function, call it when symbol changes.
  // If not, skip this section — TradingDashboard will use marketData prop.
  React.useEffect(() => {
    if (typeof subscribeToSymbol === 'function') {
      subscribeToSymbol(selectedSymbol);
      return () => {
        if (typeof unsubscribeFromSymbol === 'function') {
          unsubscribeFromSymbol(selectedSymbol);
        }
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSymbol]);

  return (
    <div className="min-h-screen bg-gray-900 text-white text-lg"> 
      
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        
        <div className="flex items-center justify-between">
          
          {/* Left: Title + WS Status */}
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-blue-400">
              AI Forex Trading Dashboard
            </h1>
            <ConnectionStatus status={connectionStatus} />
          </div>

          {/* Right: Account + Notifications */}
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <span className="text-gray-400">Account:</span>
              <span className="ml-2 text-green-400 font-semibold">
                ${accountData?.total_equity?.toLocaleString() || '0'}
              </span>
            </div>

            <NotificationCenter notifications={notifications} />
          </div>
        </div>

        {/* NEW — Symbol Switch Buttons */}
        <div className="flex space-x-3 mt-4">
          {['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'USDCAD'].map((symbol) => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedSymbol === symbol
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>

        {/* Top Navigation */}
        <nav className="flex space-x-6 mt-4">
          {[
            { id: 'dashboard', label: 'Dashboard' },
            { id: 'strategies', label: 'AI Strategies' },
            { id: 'backtesting', label: 'Backtesting' },
            { id: 'risk', label: 'Risk Management' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main */}
      <main className="p-6">

        {/* Dashboard renders the REAL chart now */}
        {activeTab === 'dashboard' && (
          <TradingDashboard 
            marketData={marketData}
            signals={signals}
            positions={positions}
            riskAssessment={riskAssessment}
            selectedSymbol={selectedSymbol}   // <-- NEW prop
          />
        )}

        {activeTab === 'strategies' && <StrategiesPanel />}
        {activeTab === 'backtesting' && <BacktestingPanel />}
        {activeTab === 'risk' && (
          <RiskManagement 
            riskAssessment={riskAssessment}
            positions={positions}
          />
        )}

      </main>

    </div>
  );
}

export default App;
