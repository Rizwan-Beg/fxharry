import { useState, useEffect } from 'react';

export function useMarketData() {
  const [accountData, setAccountData] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);

  useEffect(() => {
    // Mock account data - in production this would fetch from your API
    setAccountData({
      total_equity: 125847.50,
      available_funds: 98432.10,
      buying_power: 196864.20,
      daily_pnl: 1247.50,
      unrealized_pnl: 2156.75
    });

    // Mock positions
    setPositions([
      {
        symbol: 'EURUSD',
        quantity: 50000,
        avg_cost: 1.08234,
        market_value: 54117.00,
        unrealized_pnl: 856.50,
        currency: 'USD'
      },
      {
        symbol: 'XAUUSD',
        quantity: 2,
        avg_cost: 2018.75,
        market_value: 4040.50,
        unrealized_pnl: 3.00,
        currency: 'USD'
      }
    ]);

    // Mock risk assessment
    setRiskAssessment({
      risk_level: 0.25,
      warnings: [],
      total_exposure: 58157.50,
      exposure_ratio: 0.462,
      max_drawdown: 0.048
    });

    // Simulate periodic updates
    const interval = setInterval(() => {
      setAccountData((prev: any) => ({
        ...prev,
        daily_pnl: prev.daily_pnl + (Math.random() - 0.5) * 100,
        unrealized_pnl: prev.unrealized_pnl + (Math.random() - 0.5) * 50
      }));

      setPositions((prev: any[]) => 
        prev.map(pos => ({
          ...pos,
          unrealized_pnl: pos.unrealized_pnl + (Math.random() - 0.5) * 20
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return {
    accountData,
    positions,
    riskAssessment
  };
}