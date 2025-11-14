import React, { useMemo } from 'react';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';
import PriceChart from './PriceChart';

interface TradingChartProps {
  symbol: string;
  marketData: any;
  signals: any[];
}

// Store candles in memory (in production, use a proper state management solution)
const candleCache: { [symbol: string]: any[] } = {};

export function TradingChart({ symbol, marketData, signals }: TradingChartProps) {
  // Convert market data to candle format for lightweight-charts
  const candles = useMemo(() => {
    if (!marketData) return [];
    
    const data = marketData;
    const candle = data.candle || {};
    
    // If we have a valid candle with OHLC, add it to the cache
    if (candle.open && candle.high && candle.low && candle.close && candle.timestamp) {
      const candleKey = `${symbol}_${candle.timestamp}`;
      
      // Initialize cache for symbol if needed
      if (!candleCache[symbol]) {
        candleCache[symbol] = [];
      }
      
      // Check if this candle already exists (same timestamp)
      const existingIndex = candleCache[symbol].findIndex(
        (c: any) => c.time === candle.timestamp
      );
      
      const chartCandle = {
        time: candle.timestamp as number,
        open: candle.open as number,
        high: candle.high as number,
        low: candle.low as number,
        close: candle.close as number,
      };
      
      if (existingIndex >= 0) {
        // Update existing candle
        candleCache[symbol][existingIndex] = chartCandle;
      } else {
        // Add new candle
        candleCache[symbol].push(chartCandle);
        // Keep only last 500 candles to prevent memory issues
        if (candleCache[symbol].length > 500) {
          candleCache[symbol] = candleCache[symbol].slice(-500);
        }
      }
      
      // Sort by time
      candleCache[symbol].sort((a: any, b: any) => a.time - b.time);
    }
    
    return candleCache[symbol] || [];
  }, [marketData, symbol]);

  // Get current price for display
  const currentPrice = marketData?.mid || marketData?.close || marketData?.bid || 0;
  const bid = marketData?.bid || 0;
  const ask = marketData?.ask || 0;
  const spread = marketData?.spread || (ask > 0 && bid > 0 ? ask - bid : 0);

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-400" />
          <h3 className="text-lg font-semibold">{symbol} Chart</h3>
        </div>
        
        <div className="flex items-center space-x-4 text-sm">
          {marketData && (
            <>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Bid:</span>
                <span className="text-white">{bid.toFixed(5)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Ask:</span>
                <span className="text-white">{ask.toFixed(5)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Mid:</span>
                <span className="text-white">{currentPrice.toFixed(5)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Spread:</span>
                <span className="text-white">{spread.toFixed(5)}</span>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Real-time candlestick chart */}
      {candles.length > 0 ? (
        <PriceChart candles={candles} height={400} />
      ) : (
        <div className="w-full h-96 rounded-lg border border-gray-700 bg-gray-800 flex items-center justify-center">
          <div className="text-gray-400">Waiting for market data...</div>
        </div>
      )}
      
      {/* Chart Controls */}
      <div className="flex justify-between items-center mt-4">
        <div className="flex space-x-2">
          {['1m', '5m', '15m', '1h', '4h', '1d'].map((timeframe) => (
            <button
              key={timeframe}
              className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
            >
              {timeframe}
            </button>
          ))}
        </div>
        
        <div className="flex space-x-2 text-sm">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Price</span>
          </div>
          {signals && signals.length > 0 && (
            <>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Buy Signals</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>Sell Signals</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}