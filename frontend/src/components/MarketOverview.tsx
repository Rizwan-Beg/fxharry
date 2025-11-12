import React from 'react';
import { Globe, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface MarketOverviewProps {
  marketData: any;
}

export function MarketOverview({ marketData = {} }: MarketOverviewProps) {
  const symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'USDCAD'];
  
  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? 
      <TrendingUp className="h-4 w-4 text-green-400" /> : 
      <TrendingDown className="h-4 w-4 text-red-400" />;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center space-x-2 mb-4">
        <Globe className="h-5 w-5 text-blue-400" />
        <h3 className="text-lg font-semibold">Market Overview</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {symbols.map((symbol) => {
          const data = marketData[symbol] || {};
          const price = data.close || 0;
          const change = data.change || 0;
          const changePercent = data.change_percent || 0;
          
          return (
            <div
              key={symbol}
              className="p-3 bg-gray-700 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-gray-400" />
                  <span className="font-medium">{symbol}</span>
                </div>
                {getChangeIcon(change)}
              </div>

              <div className="space-y-1">
                <div className="text-xl font-bold">
                  {price.toFixed(5)}
                </div>
                
                <div className={`text-sm ${getChangeColor(change)}`}>
                  {change >= 0 ? '+' : ''}{change.toFixed(5)} ({changePercent.toFixed(2)}%)
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mt-2">
                  <div>
                    <span>Bid:</span>
                    <span className="ml-1 text-white">{(data.bid || 0).toFixed(5)}</span>
                  </div>
                  <div>
                    <span>Ask:</span>
                    <span className="ml-1 text-white">{(data.ask || 0).toFixed(5)}</span>
                  </div>
                  <div>
                    <span>High:</span>
                    <span className="ml-1 text-white">{(data.high || 0).toFixed(5)}</span>
                  </div>
                  <div>
                    <span>Low:</span>
                    <span className="ml-1 text-white">{(data.low || 0).toFixed(5)}</span>
                  </div>
                </div>

                {/* Mini sparkline placeholder */}
                <div className="mt-2 h-8 bg-gray-600 rounded flex items-center justify-center">
                  <Activity className="h-4 w-4 text-gray-400" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Market Status */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-gray-400">Market Open</span>
            </div>
            <div className="text-gray-400">
              New York Session
            </div>
          </div>
          
          <div className="text-gray-400">
            Updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}