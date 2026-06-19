// /src/App.tsx
import React, { useState } from 'react';
import { TradingDashboard } from './components/TradingDashboard';
import { StrategiesPanel } from './components/StrategiesPanel';
import { RiskManagement } from './components/RiskManagement';
import { BacktestingPanel } from './components/BacktestingPanel';
import { ConnectionStatus } from './components/ConnectionStatus';
import { NotificationCenter } from './components/NotificationCenter';
import { AIBrainPanel } from './components/AIBrainPanel';
import { StrategyDiagnosticsPanel } from './components/StrategyDiagnosticsPanel';
import { NewsPanel } from './components/NewsPanel';
import { useLiveFeed } from './hooks/useLiveFeed';
import { useMarketData } from './hooks/useMarketData';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isTradeHistoryOpen, setIsTradeHistoryOpen] = useState(false);

  // NEW: Selected symbol for chart switching
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD');

  const {
    marketData,
    signals,
    notifications,
    connectionStatus,
    subscribeToSymbol,
    unsubscribeFromSymbol,
    accountData,
    tradeHistory,
    aiReasoning,
    aiHistory,
    newsSentiment,
    riskAssessment,
    riskLimits,
    backtestResults,
    isBacktesting,
    strategyDiagnostics,
    rejectedSignals,
    strategies,
    send
  } = useLiveFeed();

  // We can still use useMarketData for fallback
  const {
    // accountData: mockAccountData, // Shadowed
    positions: mockPositions     // Fallback
  } = useMarketData();

  const positions = accountData?.positions || mockPositions;

  // Handler for QuickTrade
  const handleExecuteOrder = (order: any) => {
    console.log("📤 [App] Received order from QuickTradePanel:", order);
    const message = {
      type: "trade_command",
      command: "PLACE_ORDER",
      data: order
    };
    console.log("📤 [App] Sending WebSocket message:", message);
    send("trade_command", {
      command: "PLACE_ORDER",
      data: order
    });
    console.log("📤 [App] WebSocket send completed");
  };

  // Request trade history and risk limits on load/connect
  React.useEffect(() => {
    if (connectionStatus.websocket) {
      setTimeout(() => {
        send("data_command", { command: "GET_TRADE_HISTORY" });
        send("risk_command", { command: "GET_RISK_LIMITS" });
      }, 1000);
    }
  }, [connectionStatus.websocket, send]);

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
              <span className="text-gray-400">Net Liq:</span>
              <span className="ml-2 text-green-400 font-semibold">
                ${accountData?.summary?.NetLiquidation ? parseFloat(accountData.summary.NetLiquidation).toLocaleString() : '---'}
              </span>
            </div>

            <NotificationCenter notifications={notifications as any[]} />
          </div>
        </div>

        {/* NEW — Symbol Switch Buttons */}
        <div className="flex space-x-3 mt-4">
          {['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD'].map((symbol) => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedSymbol === symbol
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
            { id: 'dashboard',  label: 'Dashboard' },
            { id: 'ai_brain',   label: '🧠 AI Brain' },
            { id: 'scoring',    label: '📊 Scoring & Diagnostics' },
            { id: 'news',       label: '📰 News Feed' },
            { id: 'strategies', label: 'Strategies Hub' },
            { id: 'backtesting',label: 'Backtesting' },
            { id: 'risk',       label: 'Risk Management' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
            >
              {tab.label}
            </button>
          ))}
          {/* Trade History Button */}
          <button
            onClick={() => {
              setActiveTab('dashboard');
              setIsTradeHistoryOpen(true);
            }}
            className="px-4 py-2 rounded-lg font-medium transition-colors text-gray-400 hover:text-white hover:bg-gray-700"
          >
            Trade History
          </button>
        </nav>
      </header>

      {/* Main */}
      <main className="p-6">

        {/* Dashboard renders the REAL chart now */}
        {activeTab === 'dashboard' && (
          <TradingDashboard
            marketData={marketData}
            signals={signals}
            positions={positions} // Fallback to mock if needed, but Dashboard handles accountData.positions
            riskAssessment={riskAssessment}
            selectedSymbol={selectedSymbol}
            accountData={accountData}
            tradeHistory={tradeHistory}
            onExecuteOrder={handleExecuteOrder}
            isTradeHistoryOpen={isTradeHistoryOpen}
            onCloseTradeHistory={() => setIsTradeHistoryOpen(false)}
          />
        )}

        {activeTab === 'ai_brain' && (
          <div className="max-w-3xl mx-auto">
            <AIBrainPanel aiReasoning={aiReasoning} aiHistory={aiHistory} newsSentiment={newsSentiment} />
          </div>
        )}

        {activeTab === 'scoring' && (
          <div className="max-w-4xl mx-auto h-[80vh]">
            <StrategyDiagnosticsPanel 
              diagnostics={strategyDiagnostics} 
              rejectedSignals={rejectedSignals} 
            />
          </div>
        )}

        {activeTab === 'news' && (
          <NewsPanel newsSentiment={newsSentiment} />
        )}

        {activeTab === 'strategies' && <StrategiesPanel />}
        {activeTab === 'backtesting' && (
          <BacktestingPanel 
            backtestResults={backtestResults}
            isBacktesting={isBacktesting}
            onRunBacktest={(config) => {
              send("backtest_command", { command: "RUN_BACKTEST", data: config });
            }}
            availableStrategies={strategies}
          />
        )}
        {activeTab === 'risk' && (
          <RiskManagement
            riskAssessment={riskAssessment}
            riskLimits={riskLimits}
            onSaveRiskLimits={(limits) => {
              send("risk_command", { command: "UPDATE_RISK_LIMITS", data: limits });
            }}
            positions={positions}
          />
        )}

      </main>

    </div>
  );
}

export default App;
