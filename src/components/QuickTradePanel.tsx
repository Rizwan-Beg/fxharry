import React, { useState } from 'react';
import { Zap, Calculator, Shield, AlertTriangle } from 'lucide-react';

interface QuickTradePanelProps {
  selectedSymbol: string;
}

export function QuickTradePanel({ selectedSymbol }: QuickTradePanelProps) {
  const [tradeData, setTradeData] = useState({
    action: 'BUY',
    quantity: 10000,
    orderType: 'MKT',
    limitPrice: '',
    stopLoss: '',
    takeProfit: '',
    riskPercent: 1.0
  });

  const [positionSize, setPositionSize] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);

  const calculatePositionSize = async () => {
    // This would call your backend API
    const mockResult = {
      quantity: 8500,
      position_value: 9207.5,
      risk_amount: 85,
      risk_percent: 0.0085,
      position_size_percent: 0.092
    };
    
    setPositionSize(mockResult);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Mock risk assessment
    const mockRisk = {
      approved: tradeData.quantity <= 10000,
      risk_score: 0.3,
      warnings: tradeData.quantity > 10000 ? ['Position size exceeds recommended limit'] : [],
      risk_level: 'LOW'
    };
    
    setRiskAssessment(mockRisk);
    
    if (mockRisk.approved) {
      // Execute trade
      console.log('Executing trade:', tradeData);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center space-x-2 mb-4">
        <Zap className="h-5 w-5 text-yellow-400" />
        <h3 className="text-lg font-semibold">Quick Trade</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Symbol Display */}
        <div className="p-3 bg-gray-700 rounded-lg">
          <div className="text-center">
            <div className="text-xl font-bold text-blue-400">{selectedSymbol}</div>
            <div className="text-sm text-gray-400">Current: 1.08456</div>
          </div>
        </div>

        {/* Action Selector */}
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setTradeData({ ...tradeData, action: 'BUY' })}
            className={`py-3 px-4 rounded-lg font-medium transition-colors ${
              tradeData.action === 'BUY'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            BUY
          </button>
          <button
            type="button"
            onClick={() => setTradeData({ ...tradeData, action: 'SELL' })}
            className={`py-3 px-4 rounded-lg font-medium transition-colors ${
              tradeData.action === 'SELL'
                ? 'bg-red-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            SELL
          </button>
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Quantity
          </label>
          <input
            type="number"
            value={tradeData.quantity}
            onChange={(e) => setTradeData({ ...tradeData, quantity: Number(e.target.value) })}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="10000"
          />
        </div>

        {/* Order Type */}
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Order Type
          </label>
          <select
            value={tradeData.orderType}
            onChange={(e) => setTradeData({ ...tradeData, orderType: e.target.value })}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
          >
            <option value="MKT">Market Order</option>
            <option value="LMT">Limit Order</option>
          </select>
        </div>

        {/* Limit Price */}
        {tradeData.orderType === 'LMT' && (
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Limit Price
            </label>
            <input
              type="number"
              step="0.00001"
              value={tradeData.limitPrice}
              onChange={(e) => setTradeData({ ...tradeData, limitPrice: e.target.value })}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="1.08450"
            />
          </div>
        )}

        {/* Risk Management */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Stop Loss
            </label>
            <input
              type="number"
              step="0.00001"
              value={tradeData.stopLoss}
              onChange={(e) => setTradeData({ ...tradeData, stopLoss: e.target.value })}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="1.08200"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Take Profit
            </label>
            <input
              type="number"
              step="0.00001"
              value={tradeData.takeProfit}
              onChange={(e) => setTradeData({ ...tradeData, takeProfit: e.target.value })}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="1.08700"
            />
          </div>
        </div>

        {/* Risk Percentage */}
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Risk % of Account
          </label>
          <input
            type="number"
            step="0.1"
            value={tradeData.riskPercent}
            onChange={(e) => setTradeData({ ...tradeData, riskPercent: Number(e.target.value) })}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="1.0"
          />
        </div>

        {/* Position Size Calculator */}
        <button
          type="button"
          onClick={calculatePositionSize}
          className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <Calculator className="h-4 w-4" />
          <span>Calculate Position Size</span>
        </button>

        {/* Position Size Result */}
        {positionSize && (
          <div className="p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Calculator className="h-4 w-4 text-blue-400" />
              <span className="font-medium">Recommended Size</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-400">Quantity:</span>
                <div className="font-medium">{positionSize.quantity.toLocaleString()}</div>
              </div>
              <div>
                <span className="text-gray-400">Risk Amount:</span>
                <div className="font-medium">${positionSize.risk_amount}</div>
              </div>
            </div>
          </div>
        )}

        {/* Risk Assessment */}
        {riskAssessment && (
          <div className={`p-3 rounded-lg border ${
            riskAssessment.approved 
              ? 'bg-green-900 border-green-700' 
              : 'bg-red-900 border-red-700'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              {riskAssessment.approved ? (
                <Shield className="h-4 w-4 text-green-400" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-red-400" />
              )}
              <span className="font-medium">
                Risk Assessment: {riskAssessment.risk_level}
              </span>
            </div>
            {riskAssessment.warnings.length > 0 && (
              <ul className="text-sm space-y-1">
                {riskAssessment.warnings.map((warning: string, index: number) => (
                  <li key={index} className="flex items-center space-x-1">
                    <span>•</span>
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            tradeData.action === 'BUY'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
        >
          Execute {tradeData.action} Order
        </button>
      </form>
    </div>
  );
}