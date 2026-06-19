import { useState, useEffect } from 'react';
import { Brain, Play, Pause, Upload, Settings, TrendingUp, BarChart3, CloudLightning } from 'lucide-react';
import { createWS } from '../services/ws';
import { StrategyCodeModal } from './StrategyCodeModal';

export function StrategiesPanel() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [wsService, setWsService] = useState<any>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);
  const [isCodeModalOpen, setIsCodeModalOpen] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = createWS();
    setWsService(ws);

    // Listen for strategy status updates
    ws.on('strategy_status', (data: any[]) => {
      console.log('Received strategy status update:', data);

      // Map backend data to UI format
      const formattedStrategies = data.map(s => ({
        id: s.id,
        name: s.name,
        description: s.description,
        strategy_type: s.id === 'riztest' ? 'test' : 'python', // Simple mapping for now
        is_active: s.is_active,
        total_trades: 0, // Backend doesn't send this yet
        winning_trades: 0,
        total_pnl: 0,
        sharpe_ratio: 0,
        max_drawdown: 0
      }));

      setStrategies(formattedStrategies);
    });

    // Request initial status when connected
    ws.ws.onopen = () => {
      console.log('Requesting initial strategy status...');
      ws.send('strategy_command', {
        command: 'GET_STRATEGY_STATUS'
      });
    };

    return () => {
      ws.ws.close();
    };
  }, []);

  const toggleStrategy = (strategyId: string, currentState: boolean) => {
    if (!wsService) return;

    const command = currentState ? 'DEACTIVATE_STRATEGY' : 'ACTIVATE_STRATEGY';
    console.log(`Sending ${command} for ${strategyId}`);

    wsService.send('strategy_command', {
      command: command,
      strategy_id: strategyId
    });

    // Optimistic update (will be overwritten by WS response)
    setStrategies(prev =>
      prev.map(strategy =>
        strategy.id === strategyId
          ? { ...strategy, is_active: !strategy.is_active }
          : strategy
      )
    );
  };

  const handleConfigureClick = (strategy: any) => {
    setSelectedStrategy(strategy);
    setIsCodeModalOpen(true);
  };

  const getStrategyTypeIcon = (type: string) => {
    switch (type) {
      case 'ml_model':
        return <Brain className="h-4 w-4 text-purple-400" />;
      case 'python':
        return <BarChart3 className="h-4 w-4 text-blue-400" />;
      case 'cpp':
        return <TrendingUp className="h-4 w-4 text-green-400" />;
      case 'test':
        return <CloudLightning className="h-4 w-4 text-yellow-400" />;
      default:
        return <Settings className="h-4 w-4 text-gray-400" />;
    }
  };

  const getWinRate = (strategy: any) => {
    return strategy.total_trades > 0
      ? (strategy.winning_trades / strategy.total_trades * 100).toFixed(1)
      : '0.0';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="h-6 w-6 text-purple-400" />
          <h2 className="text-2xl font-bold">Trading Strategies</h2>
        </div>

        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            <Upload className="h-4 w-4" />
            <span>Upload Strategy</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Active Strategies Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Strategies</p>
              <p className="text-2xl font-bold text-green-400">
                {strategies.filter(s => s.is_active).length}
              </p>
            </div>
            <Play className="h-8 w-8 text-green-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Strategies</p>
              <p className="text-2xl font-bold text-blue-400">
                {strategies.length}
              </p>
            </div>
            <Brain className="h-8 w-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Combined P&L</p>
              <p className="text-2xl font-bold text-green-400">
                ${strategies.reduce((sum, s) => sum + (s.total_pnl || 0), 0).toFixed(2)}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-400" />
          </div>
        </div>
      </div>

      {/* Strategies List */}
      <div className="space-y-4">
        {strategies.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            Waiting for strategy data from backend...
          </div>
        ) : (
          strategies.map((strategy) => (
            <div
              key={strategy.id}
              className={`bg-gray-800 rounded-lg p-6 border transition-colors ${strategy.is_active
                ? 'border-green-500 bg-green-900/10'
                : 'border-gray-700 hover:border-gray-600'
                }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStrategyTypeIcon(strategy.strategy_type)}
                  <div>
                    <h3 className="text-lg font-semibold">{strategy.name} <span className="text-xs text-gray-500">({strategy.id})</span></h3>
                    <p className="text-sm text-gray-400">{strategy.description}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${strategy.is_active
                    ? 'bg-green-900 text-green-400'
                    : 'bg-gray-700 text-gray-400'
                    }`}>
                    {strategy.is_active ? 'ACTIVE' : 'INACTIVE'}
                  </span>

                  <button
                    onClick={() => toggleStrategy(strategy.id, strategy.is_active)}
                    className={`p-2 rounded-lg transition-colors ${strategy.is_active
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                      }`}
                  >
                    {strategy.is_active ? (
                      <Pause className="h-4 w-4" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Performance Metrics (Placeholder for now) */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 opacity-50">
                <div className="text-center">
                  <div className="text-sm text-gray-400">Total Trades</div>
                  <div className="text-lg font-semibold">{strategy.total_trades || 0}</div>
                </div>

                <div className="text-center">
                  <div className="text-sm text-gray-400">Win Rate</div>
                  <div className="text-lg font-semibold text-green-400">
                    {getWinRate(strategy)}%
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-sm text-gray-400">Total P&L</div>
                  <div className={`text-lg font-semibold ${strategy.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                    ${(strategy.total_pnl || 0).toFixed(2)}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-sm text-gray-400">Sharpe Ratio</div>
                  <div className="text-lg font-semibold text-blue-400">
                    {(strategy.sharpe_ratio || 0).toFixed(2)}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-sm text-gray-400">Max Drawdown</div>
                  <div className="text-lg font-semibold text-red-400">
                    {((strategy.max_drawdown || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="mt-2 text-xs text-center text-gray-500 italic">
                * Performance metrics coming soon from database
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 mt-4">
                <button className="flex-1 py-2 px-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
                  View Details
                </button>
                <button className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                  Backtest
                </button>
                <button
                  onClick={() => handleConfigureClick(strategy)}
                  className="flex-1 py-2 px-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                >
                  Configure
                </button>
              </div>
            </div>
          )))}
      </div>

      {/* Strategy Code Modal */}
      {selectedStrategy && (
        <StrategyCodeModal
          isOpen={isCodeModalOpen}
          onClose={() => setIsCodeModalOpen(false)}
          strategyId={selectedStrategy.id}
          strategyName={selectedStrategy.name}
        />
      )}

    </div>
  );
}