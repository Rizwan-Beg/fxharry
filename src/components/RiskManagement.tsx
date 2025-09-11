import React, { useState } from 'react';
import { Shield, AlertTriangle, Settings, TrendingDown, DollarSign } from 'lucide-react';

interface RiskManagementProps {
  riskAssessment: any;
  positions: any[];
}

export function RiskManagement({ riskAssessment, positions }: RiskManagementProps) {
  const [riskLimits, setRiskLimits] = useState({
    maxDailyLoss: 2.0,
    maxPositionSize: 5.0,
    maxCorrelationExposure: 15.0,
    maxDrawdownLimit: 20.0
  });

  const [showSettings, setShowSettings] = useState(false);

  const updateRiskLimit = (key: string, value: number) => {
    setRiskLimits(prev => ({ ...prev, [key]: value }));
  };

  const getRiskLevelColor = (level: number) => {
    if (level <= 0.3) return 'text-green-400';
    if (level <= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskLevelBg = (level: number) => {
    if (level <= 0.3) return 'bg-green-900 border-green-700';
    if (level <= 0.6) return 'bg-yellow-900 border-yellow-700';
    return 'bg-red-900 border-red-700';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="h-6 w-6 text-blue-400" />
          <h2 className="text-2xl font-bold">Risk Management</h2>
        </div>
        
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </button>
      </div>

      {/* Risk Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Portfolio Risk</p>
              <p className={`text-2xl font-bold ${getRiskLevelColor(riskAssessment?.risk_level || 0)}`}>
                {riskAssessment?.risk_level ? (riskAssessment.risk_level * 100).toFixed(0) : '0'}%
              </p>
            </div>
            <Shield className={`h-8 w-8 ${getRiskLevelColor(riskAssessment?.risk_level || 0)}`} />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Exposure</p>
              <p className="text-2xl font-bold text-blue-400">
                ${(riskAssessment?.total_exposure || 0).toLocaleString()}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Exposure Ratio</p>
              <p className="text-2xl font-bold text-yellow-400">
                {((riskAssessment?.exposure_ratio || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <TrendingDown className="h-8 w-8 text-yellow-400" />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Max Drawdown</p>
              <p className="text-2xl font-bold text-red-400">
                {((riskAssessment?.max_drawdown || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Risk Warnings */}
      {riskAssessment?.warnings && riskAssessment.warnings.length > 0 && (
        <div className={`rounded-lg p-4 border ${getRiskLevelBg(riskAssessment.risk_level || 0)}`}>
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            <h3 className="text-lg font-semibold">Risk Warnings</h3>
          </div>
          <ul className="space-y-2">
            {riskAssessment.warnings.map((warning: string, index: number) => (
              <li key={index} className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Settings */}
      {showSettings && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Risk Limits Configuration</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Max Daily Loss (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={riskLimits.maxDailyLoss}
                onChange={(e) => updateRiskLimit('maxDailyLoss', Number(e.target.value))}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Max Position Size (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={riskLimits.maxPositionSize}
                onChange={(e) => updateRiskLimit('maxPositionSize', Number(e.target.value))}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Max Correlation Exposure (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={riskLimits.maxCorrelationExposure}
                onChange={(e) => updateRiskLimit('maxCorrelationExposure', Number(e.target.value))}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Max Drawdown Limit (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={riskLimits.maxDrawdownLimit}
                onChange={(e) => updateRiskLimit('maxDrawdownLimit', Number(e.target.value))}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              Save Settings
            </button>
            <button className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              Reset to Defaults
            </button>
          </div>
        </div>
      )}

      {/* Position Risk Analysis */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Position Risk Analysis</h3>
        
        {positions && positions.length > 0 ? (
          <div className="space-y-3">
            {positions.map((position, index) => {
              const riskScore = Math.random() * 0.8; // Mock risk score
              return (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{position.symbol}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        position.quantity > 0 ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                      }`}>
                        {position.quantity > 0 ? 'LONG' : 'SHORT'}
                      </span>
                    </div>
                    <div className={`text-sm font-medium ${getRiskLevelColor(riskScore)}`}>
                      Risk: {(riskScore * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Size:</span>
                      <div className="font-medium">{Math.abs(position.quantity).toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Value:</span>
                      <div className="font-medium">${Math.abs(position.market_value).toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">P&L:</span>
                      <div className={`font-medium ${
                        position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        ${position.unrealized_pnl.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-600 mx-auto mb-2" />
            <p className="text-gray-400">No open positions to analyze</p>
          </div>
        )}
      </div>

      {/* Risk Metrics Chart Placeholder */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Risk Metrics Over Time</h3>
        <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <TrendingDown className="h-12 w-12 text-gray-500 mx-auto mb-2" />
            <p className="text-gray-400">Risk metrics chart will be displayed here</p>
          </div>
        </div>
      </div>
    </div>
  );
}