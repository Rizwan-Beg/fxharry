import React, { useState, useEffect } from 'react';
import { TradingDashboard } from './components/TradingDashboard';
import { StrategiesPanel } from './components/StrategiesPanel';
import { RiskManagement } from './components/RiskManagement';
import { BacktestingPanel } from './components/BacktestingPanel';
import { ConnectionStatus } from './components/ConnectionStatus';
import { NotificationCenter } from './components/NotificationCenter';
import { useWebSocket } from './hooks/useWebSocket';
import { useMarketData } from './hooks/useMarketData';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { 
    marketData, 
    signals, 
    notifications, 
    connectionStatus 
  } = useWebSocket('ws://localhost:8000/ws');
  
  const { 
    accountData, 
    positions, 
    riskAssessment 
  } = useMarketData();

  return (
    <div className="min-h-screen bg-gray-900 text-white text-lg"> 
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-blue-400">
              AI Forex Trading Dashboard
            </h1>
            <ConnectionStatus status={connectionStatus} />
          </div>
          
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

        {/* Navigation */}
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

      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'dashboard' && (
          <TradingDashboard 
            marketData={marketData}
            signals={signals}
            positions={positions}
            riskAssessment={riskAssessment}
          />
        )}
        
        {activeTab === 'strategies' && (
          <StrategiesPanel />
        )}
        
        {activeTab === 'backtesting' && (
          <BacktestingPanel />
        )}
        
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