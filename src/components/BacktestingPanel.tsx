import React, { useState } from 'react';
import { BarChart3, Play, Calendar, DollarSign, TrendingUp, Download } from 'lucide-react';

export function BacktestingPanel() {
  const [backtestConfig, setBacktestConfig] = useState({
    strategyId: 1,
    startDate: '2024-01-01',
    endDate: '2024-12-01',
    initialCapital: 100000,
    symbols: ['EURUSD', 'GBPUSD', 'XAUUSD']
  });

  const [backtestResults, setBacktestResults] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);

  const mockResults = {
    initial_capital: 100000,
    final_capital: 125847.50,
    total_return: 0.25847,
    total_trades: 234,
    winning_trades: 156,
    losing_trades: 78,
    win_rate: 0.667,
    profit_factor: 1.85,
    sharpe_ratio: 1.42,
    max_drawdown: 0.087,
    avg_trade_duration: 4.2
  };

  const runBacktest = async () => {
    setIsRunning(true);
    
    // Simulate API call
    setTimeout(() => {
      setBacktestResults(mockResults);
      setIsRunning(false);
    }, 3000);
  };

  const strategies = [
    { id: 1, name: 'LSTM Forex Predictor' },
    { id: 2, name: 'Mean Reversion Strategy' },
    { id: 3, name: 'High-Frequency Scalper' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-6 w-6 text-green-400" />
          <h2 className="text-2xl font-bold">Strategy Backtesting</h2>
        </div>
      </div>

      {/* Backtest Configuration */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Backtest Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Strategy
            </label>
            <select
              value={backtestConfig.strategyId}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, strategyId: Number(e.target.value) }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              {strategies.map(strategy => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Initial Capital ($)
            </label>
            <input
              type="number"
              value={backtestConfig.initialCapital}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, initialCapital: Number(e.target.value) }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={backtestConfig.startDate}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, startDate: e.target.value }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={backtestConfig.endDate}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, endDate: e.target.value }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Trading Symbols
          </label>
          <div className="flex flex-wrap gap-2">
            {['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'USDCAD'].map(symbol => (
              <label key={symbol} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={backtestConfig.symbols.includes(symbol)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setBacktestConfig(prev => ({ 
                        ...prev, 
                        symbols: [...prev.symbols, symbol] 
                      }));
                    } else {
                      setBacktestConfig(prev => ({ 
                        ...prev, 
                        symbols: prev.symbols.filter(s => s !== symbol) 
                      }));
                    }
                  }}
                  className="rounded"
                />
                <span className="text-sm">{symbol}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="flex space-x-3 mt-6">
          <button
            onClick={runBacktest}
            disabled={isRunning}
            className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg transition-colors"
          >
            <Play className="h-4 w-4" />
            <span>{isRunning ? 'Running...' : 'Run Backtest'}</span>
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isRunning && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Running Backtest</h3>
            <p className="text-gray-400">Processing historical data and executing strategy...</p>
          </div>
        </div>
      )}

      {/* Backtest Results */}
      {backtestResults && (
        <div className="space-y-6">
          {/* Performance Summary */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Performance Summary</h3>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                <Download className="h-4 w-4" />
                <span>Export Results</span>
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  ${backtestResults.final_capital.toLocaleString()}
                </div>
                <div className="text-sm text-gray-400">Final Capital</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  {(backtestResults.total_return * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-400">Total Return</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {(backtestResults.win_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-400">Win Rate</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {backtestResults.sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-400">Sharpe Ratio</div>
              </div>
            </div>
          </div>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h4 className="text-lg font-semibold mb-4">Trade Statistics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Trades:</span>
                  <span className="font-medium">{backtestResults.total_trades}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Winning Trades:</span>
                  <span className="font-medium text-green-400">{backtestResults.winning_trades}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Losing Trades:</span>
                  <span className="font-medium text-red-400">{backtestResults.losing_trades}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Profit Factor:</span>
                  <span className="font-medium">{backtestResults.profit_factor.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Trade Duration:</span>
                  <span className="font-medium">{backtestResults.avg_trade_duration.toFixed(1)}h</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h4 className="text-lg font-semibold mb-4">Risk Metrics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Drawdown:</span>
                  <span className="font-medium text-red-400">
                    {(backtestResults.max_drawdown * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sharpe Ratio:</span>
                  <span className="font-medium">{backtestResults.sharpe_ratio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Initial Capital:</span>
                  <span className="font-medium">${backtestResults.initial_capital.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Final Capital:</span>
                  <span className="font-medium text-green-400">
                    ${backtestResults.final_capital.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Net Profit:</span>
                  <span className="font-medium text-green-400">
                    ${(backtestResults.final_capital - backtestResults.initial_capital).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Equity Curve Placeholder */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h4 className="text-lg font-semibold mb-4">Equity Curve</h4>
            <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400">Equity curve chart will be displayed here</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}