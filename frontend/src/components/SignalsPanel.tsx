import React from 'react';
import { Brain, TrendingUp, TrendingDown, Zap } from 'lucide-react';

interface SignalsPanelProps {
  signals: any[];
}

export function SignalsPanel({ signals = [] }: SignalsPanelProps) {
  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp className="h-4 w-4 text-green-400" />;
      case 'SELL':
        return <TrendingDown className="h-4 w-4 text-red-400" />;
      default:
        return <Zap className="h-4 w-4 text-yellow-400" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="h-5 w-5 text-purple-400" />
          <h3 className="text-lg font-semibold">AI Signals</h3>
        </div>
        <span className="text-sm text-gray-400">
          {signals.length} active
        </span>
      </div>

      <div className="space-y-3">
        {signals.length === 0 ? (
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-600 mx-auto mb-2" />
            <p className="text-gray-400">No active signals</p>
            <p className="text-sm text-gray-500">AI models are analyzing market conditions</p>
          </div>
        ) : (
          signals.map((signal, index) => (
            <div
              key={index}
              className="p-3 bg-gray-700 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getSignalIcon(signal.signal)}
                  <span className="font-medium">{signal.symbol}</span>
                  <span className={`text-sm font-semibold ${
                    signal.signal === 'BUY' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {signal.signal}
                  </span>
                </div>
                <span className={`text-sm font-medium ${getConfidenceColor(signal.confidence)}`}>
                  {(signal.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <div>
                  <span>Strategy:</span>
                  <span className="ml-1 text-white">AI-{signal.strategy_id}</span>
                </div>
                <div>
                  <span>Time:</span>
                  <span className="ml-1 text-white">
                    {new Date(signal.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="mt-2">
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      signal.confidence >= 0.8 ? 'bg-green-400' :
                      signal.confidence >= 0.6 ? 'bg-yellow-400' : 'bg-orange-400'
                    }`}
                    style={{ width: `${signal.confidence * 100}%` }}
                  />
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-3 flex space-x-2">
                <button className="flex-1 py-1.5 px-3 bg-blue-600 hover:bg-blue-700 rounded-md text-sm font-medium transition-colors">
                  Execute Trade
                </button>
                <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 rounded-md text-sm font-medium transition-colors">
                  View Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Stats */}
      {signals.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <div className="text-green-400 font-semibold">
                {signals.filter(s => s.signal === 'BUY').length}
              </div>
              <div className="text-gray-400">Buy</div>
            </div>
            <div>
              <div className="text-red-400 font-semibold">
                {signals.filter(s => s.signal === 'SELL').length}
              </div>
              <div className="text-gray-400">Sell</div>
            </div>
            <div>
              <div className="text-blue-400 font-semibold">
                {(signals.reduce((acc, s) => acc + s.confidence, 0) / signals.length * 100).toFixed(0)}%
              </div>
              <div className="text-gray-400">Avg Confidence</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}