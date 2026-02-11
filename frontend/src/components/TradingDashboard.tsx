import React, { useState, useEffect } from 'react';
import { TradingChart } from './TradingChart';
import { SignalsPanel } from './SignalsPanel';
import { PositionsPanel } from './PositionsPanel';
import { MarketOverview } from './MarketOverview';
import { QuickTradePanel } from './QuickTradePanel';
import { TradeHistoryPanel } from './TradeHistoryPanel';
import { RiskIndicator } from './RiskIndicator';
import PriceChart from "./PriceChart";
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle } from 'lucide-react';

interface TradingDashboardProps {
  marketData: any;
  signals: any[];
  positions: any[];
  riskAssessment: any;
  selectedSymbol?: string;
  accountData?: any;
  tradeHistory?: any[];
  onExecuteOrder?: (order: any) => void;
}

export function TradingDashboard({
  marketData,
  signals,
  positions,
  riskAssessment,
  selectedSymbol: propSelectedSymbol,
  accountData,
  tradeHistory,
  onExecuteOrder
}: TradingDashboardProps) {
  const [selectedSymbol, setSelectedSymbol] = useState(propSelectedSymbol || 'EURUSD');

  // Update local state if prop changes
  useEffect(() => {
    if (propSelectedSymbol) {
      setSelectedSymbol(propSelectedSymbol);
    }
  }, [propSelectedSymbol]);

  const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD']; // XAUUSD commented out - will fix later

  return (
    <div className="space-y-6">
      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Daily P&L</p>
              <p className={`text-2xl font-bold ${(parseFloat(accountData?.summary?.RealizedPnL || '0') + parseFloat(accountData?.summary?.UnrealizedPnL || '0')) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${accountData?.summary?.RealizedPnL || accountData?.summary?.UnrealizedPnL ? 
                  (parseFloat(accountData.summary.RealizedPnL || '0') + parseFloat(accountData.summary.UnrealizedPnL || '0')).toFixed(2) : '0.00'}
              </p>
              <div className="text-xs text-gray-500 mt-1">
                Realized: ${accountData?.summary?.RealizedPnL || '0.00'} | Unrealized: ${accountData?.summary?.UnrealizedPnL || '0.00'}
              </div>
            </div>
            {(parseFloat(accountData?.summary?.RealizedPnL || '0') + parseFloat(accountData?.summary?.UnrealizedPnL || '0')) >= 0 ? 
              <TrendingUp className="h-8 w-8 text-green-400" /> : 
              <TrendingDown className="h-8 w-8 text-red-400" />}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Open Positions</p>
              <p className="text-2xl font-bold text-blue-400">
                {positions?.length || 0}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Signals</p>
              <p className="text-2xl font-bold text-purple-400">
                {signals?.length || 0}
              </p>
            </div>
            <TrendingDown className="h-8 w-8 text-purple-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <RiskIndicator
            riskLevel={riskAssessment?.risk_level || 0}
            warnings={riskAssessment?.warnings || []}
          />
        </div>
      </div>

      {/* Main Trading Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Area */}
        <div className="lg:col-span-2 space-y-4">
          {/* Symbol Selector */}
          <div className="flex space-x-2">
            {symbols.map((symbol) => (
              <button
                key={symbol}
                onClick={() => setSelectedSymbol(symbol)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedSymbol === symbol
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
              >
                {symbol}
              </button>
            ))}
          </div>

          {/* Trading Chart */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <TradingChart
              symbol={selectedSymbol}
              marketData={marketData?.[selectedSymbol]}
              signals={signals?.filter(s => s.symbol === selectedSymbol)}
            />
          </div>

          {/* Market Overview */}
          <MarketOverview marketData={marketData} />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Trade Panel */}
          <QuickTradePanel
            selectedSymbol={selectedSymbol}
            onExecuteOrder={onExecuteOrder || (() => { })}
          />

          {/* AI Signals */}
          <SignalsPanel signals={signals} />

          {/* Positions */}
          <PositionsPanel positions={accountData?.positions || positions} />
          
          {/* Trade History - Moved to sidebar */}
          <TradeHistoryPanel trades={tradeHistory || []} />
        </div>
      </div>
    </div>
  );
}