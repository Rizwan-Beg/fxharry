import React from 'react';
import { Shield, AlertTriangle, AlertCircle } from 'lucide-react';

interface RiskIndicatorProps {
  riskLevel: number;
  warnings: string[];
}

export function RiskIndicator({ riskLevel, warnings }: RiskIndicatorProps) {
  const getRiskColor = () => {
    if (riskLevel <= 0.3) return 'text-green-400';
    if (riskLevel <= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskIcon = () => {
    if (riskLevel <= 0.3) return <Shield className="h-8 w-8 text-green-400" />;
    if (riskLevel <= 0.6) return <AlertTriangle className="h-8 w-8 text-yellow-400" />;
    return <AlertCircle className="h-8 w-8 text-red-400" />;
  };

  const getRiskLabel = () => {
    if (riskLevel <= 0.3) return 'LOW';
    if (riskLevel <= 0.6) return 'MEDIUM';
    return 'HIGH';
  };

  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm">Portfolio Risk</p>
        <p className={`text-2xl font-bold ${getRiskColor()}`}>
          {getRiskLabel()}
        </p>
        {warnings.length > 0 && (
          <p className="text-xs text-red-400 mt-1">
            {warnings.length} warning{warnings.length > 1 ? 's' : ''}
          </p>
        )}
      </div>
      {getRiskIcon()}
    </div>
  );
}