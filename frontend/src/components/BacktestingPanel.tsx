import React, { useState } from 'react';
import { BarChart3, Play, Calendar, DollarSign, TrendingUp, Download } from 'lucide-react';

interface BacktestingPanelProps {
  backtestResults?: any;
  isBacktesting?: boolean;
  onRunBacktest?: (config: any) => void;
  availableStrategies?: any[];
}

export function BacktestingPanel({ backtestResults, isBacktesting, onRunBacktest, availableStrategies = [] }: BacktestingPanelProps) {
  const [backtestConfig, setBacktestConfig] = useState({
    strategyId: availableStrategies.length > 0 ? availableStrategies[0].id : 'apex',
    startDate: '2025-01-01',
    endDate: '2025-02-01',
    initialCapital: 100000,
    symbols: ['EURUSD'],
    timeframe: '1h',
    slStop: 0.02,
    tpStop: 0.06,
    fees: 0.0001,
    leverage: 1
  });

  const runBacktest = () => {
    if (onRunBacktest) {
      onRunBacktest(backtestConfig);
    }
  };

  const strategies = availableStrategies.length > 0 ? availableStrategies : [
    { id: 'apex', name: 'Apex Multi-Timeframe' },
    { id: 'smc', name: 'Smart Money Concepts' },
    { id: 'ml', name: 'ML Predictor' },
    { id: 'riztest', name: 'RizTest Strategy' }
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
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, strategyId: e.target.value }))}
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

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Timeframe
            </label>
            <select
              value={backtestConfig.timeframe}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, timeframe: e.target.value }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value="1m">1 Minute</option>
              <option value="5m">5 Minutes</option>
              <option value="15m">15 Minutes</option>
              <option value="1h">1 Hour</option>
              <option value="4h">4 Hours</option>
              <option value="1d">1 Day</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Stop Loss (%)
            </label>
            <input
              type="number"
              step="0.01"
              value={backtestConfig.slStop * 100}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, slStop: Number(e.target.value) / 100 }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Take Profit (%)
            </label>
            <input
              type="number"
              step="0.01"
              value={backtestConfig.tpStop * 100}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, tpStop: Number(e.target.value) / 100 }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Fees/Spread (%)
            </label>
            <input
              type="number"
              step="0.001"
              value={backtestConfig.fees * 100}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, fees: Number(e.target.value) / 100 }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Margin Leverage
            </label>
            <select
              value={backtestConfig.leverage}
              onChange={(e) => setBacktestConfig(prev => ({ ...prev, leverage: Number(e.target.value) }))}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value={1}>1:1 (No Leverage)</option>
              <option value={10}>10:1 (10x Margin)</option>
              <option value={30}>30:1 (30x Margin)</option>
              <option value={50}>50:1 (50x Margin)</option>
              <option value={100}>100:1 (100x Margin)</option>
            </select>
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
            disabled={isBacktesting}
            className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg transition-colors"
          >
            <Play className="h-4 w-4" />
            <span>{isBacktesting ? 'Running VectorBT...' : 'Run VectorBT Backtest'}</span>
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isBacktesting && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Running Backtest</h3>
            <p className="text-gray-400">Processing historical data and executing strategy...</p>
          </div>
        </div>
      )}

      {/* Backtest Results */}
      {backtestResults && backtestResults.error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-400 mb-2">Backtest Engine Error</h3>
          <p className="text-gray-300">{backtestResults.error}</p>
          <p className="text-gray-400 text-sm mt-4">Tip: Check if your date range has data or if the symbol is valid.</p>
        </div>
      )}

      {backtestResults && !backtestResults.error && (
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
            </div>

            {/* Detailed Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t border-gray-700">
              <div>
                <div className="text-sm text-gray-400">Profit Factor</div>
                <div className="text-lg font-semibold">{backtestResults.profit_factor?.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Max Drawdown</div>
                <div className="text-lg font-semibold text-red-400">
                  {(backtestResults.max_drawdown * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Avg Trade Duration</div>
                <div className="text-lg font-semibold">{backtestResults.average_trade_duration?.toFixed(1)}h</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Sharpe Ratio</div>
                <div className="text-lg font-semibold">{backtestResults.sharpe_ratio?.toFixed(2)}</div>
              </div>
            </div>
          </div>

          {/* Broker Cost Analysis */}
          {backtestResults.gross_profit !== undefined && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4 text-orange-400 flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                Broker Cost Analysis (IBKR Simulation)
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Cost Breakdown */}
                <div className="space-y-4">
                  <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                    <span className="text-gray-400">Gross Profit Before Costs</span>
                    <span className="font-medium text-green-400">+${backtestResults.gross_profit.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                    <span className="text-gray-400">Total Commission Paid</span>
                    <span className="font-medium text-red-400">-${backtestResults.total_fees_paid.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                    <span className="text-gray-400">Total Slippage Cost</span>
                    <span className="font-medium text-red-400">-${backtestResults.total_slippage_cost.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-bold text-white">Net Profit After Costs</span>
                    <span className={`font-bold ${backtestResults.net_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {backtestResults.net_profit >= 0 ? '+' : ''}${backtestResults.net_profit.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Average Commission Per Trade: ${backtestResults.avg_commission_per_trade.toFixed(2)}
                  </div>
                </div>

                {/* Return Impact Analysis */}
                <div className="bg-gray-900 rounded-lg p-4 space-y-3 border border-gray-700">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Gross Return</span>
                    <span className="font-medium text-green-400">+{backtestResults.gross_return_pct.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Commission Impact</span>
                    <span className="font-medium text-red-400">-{backtestResults.commission_impact_pct.toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Slippage Impact</span>
                    <span className="font-medium text-red-400">-{backtestResults.slippage_impact_pct.toFixed(2)}%</span>
                  </div>
                  <div className="h-px bg-gray-700 w-full my-2"></div>
                  <div className="flex justify-between items-center">
                    <span className="font-bold">Net Return</span>
                    <span className={`font-bold ${backtestResults.net_return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {backtestResults.net_return_pct >= 0 ? '+' : ''}{backtestResults.net_return_pct.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

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