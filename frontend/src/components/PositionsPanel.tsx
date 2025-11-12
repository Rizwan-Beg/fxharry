import React from 'react';
import { PieChart, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

interface PositionsPanelProps {
  positions: any[];
}

export function PositionsPanel({ positions = [] }: PositionsPanelProps) {
  const totalPnL = positions.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0);
  const totalValue = positions.reduce((sum, pos) => sum + Math.abs(pos.market_value || 0), 0);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <PieChart className="h-5 w-5 text-green-400" />
          <h3 className="text-lg font-semibold">Open Positions</h3>
        </div>
        <span className="text-sm text-gray-400">
          {positions.length} positions
        </span>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 bg-gray-700 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Total P&L</span>
            <DollarSign className="h-4 w-4 text-gray-400" />
          </div>
          <div className={`text-lg font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${totalPnL.toFixed(2)}
          </div>
        </div>

        <div className="p-3 bg-gray-700 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Total Value</span>
            <PieChart className="h-4 w-4 text-gray-400" />
          </div>
          <div className="text-lg font-bold text-white">
            ${totalValue.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Positions List */}
      <div className="space-y-3">
        {positions.length === 0 ? (
          <div className="text-center py-8">
            <PieChart className="h-12 w-12 text-gray-600 mx-auto mb-2" />
            <p className="text-gray-400">No open positions</p>
            <p className="text-sm text-gray-500">Your positions will appear here</p>
          </div>
        ) : (
          positions.map((position, index) => (
            <div
              key={index}
              className="p-3 bg-gray-700 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {position.quantity > 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-400" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-400" />
                  )}
                  <span className="font-medium">{position.symbol}</span>
                  <span className={`text-sm px-2 py-1 rounded text-xs font-medium ${
                    position.quantity > 0 
                      ? 'bg-green-900 text-green-400' 
                      : 'bg-red-900 text-red-400'
                  }`}>
                    {position.quantity > 0 ? 'LONG' : 'SHORT'}
                  </span>
                </div>
                
                <div className="text-right">
                  <div className={`text-sm font-medium ${
                    (position.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    ${(position.unrealized_pnl || 0).toFixed(2)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {((position.unrealized_pnl || 0) / Math.abs(position.market_value || 1) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
                <div>
                  <span>Size:</span>
                  <div className="text-white font-medium">
                    {Math.abs(position.quantity || 0).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span>Avg Cost:</span>
                  <div className="text-white font-medium">
                    {(position.avg_cost || 0).toFixed(5)}
                  </div>
                </div>
                <div>
                  <span>Market Value:</span>
                  <div className="text-white font-medium">
                    ${Math.abs(position.market_value || 0).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-3 flex space-x-2">
                <button className="flex-1 py-1.5 px-3 bg-red-600 hover:bg-red-700 rounded-md text-sm font-medium transition-colors">
                  Close Position
                </button>
                <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 rounded-md text-sm font-medium transition-colors">
                  Modify
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      {positions.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <button className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors">
            Close All Positions
          </button>
        </div>
      )}
    </div>
  );
}