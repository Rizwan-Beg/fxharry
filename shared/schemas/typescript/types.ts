export type Position = {
  symbol: string;
  quantity: number;
  avg_price: number;
  market_value: number;
};

export type AccountSummary = {
  status: string;
  timestamp: string;
  broker: string;
  total_equity: number;
  available_funds: number;
  buying_power: number;
  positions: Position[];
};

export type MarketDataUpdate = {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  timestamp: string;
};

export type AISignal = {
  symbol: string;
  signal_type: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  timestamp: string;
};