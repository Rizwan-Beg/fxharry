import React, { useMemo } from 'react';
import { Activity } from 'lucide-react';
import PriceChart from './PriceChart';

interface TradingChartProps {
  symbol: string;
  marketData: any;
  signals: any[];
}

// Store candles in memory (in production, use a proper state management solution)
const candleCache: { [symbol: string]: any[] } = {};

export function TradingChart({ symbol, marketData, signals }: TradingChartProps) {
  // Debug: Log when marketData changes (reduced frequency)
  React.useEffect(() => {
    if (marketData) {
      const hasCandle = !!marketData.candle;
      const candleValid = hasCandle && 
        typeof marketData.candle.open === 'number' && 
        typeof marketData.candle.timestamp === 'number';
      
      // Only log every 10th update to reduce console spam
      const shouldLog = Math.random() < 0.1; // 10% chance
      if (shouldLog) {
        console.log(`[TradingChart] ${symbol} marketData:`, {
          hasCandle,
          candleValid,
          bid: marketData.bid,
          ask: marketData.ask,
          mid: marketData.mid,
          candlesCount: candleCache[symbol]?.length || 0,
          hasCandleData: !!marketData.candle?.timestamp
        });
      }
    } else {
      console.log(`[TradingChart] ${symbol} - No marketData`);
    }
  }, [marketData, symbol]);

  // Convert market data to candle format for lightweight-charts
  const candles = useMemo(() => {
    if (!marketData) {
      console.log(`[TradingChart] No marketData for ${symbol}`);
      return [];
    }
    
    const data = marketData;
    const candle = (data.candle && typeof data.candle.timestamp === 'number' && typeof data.candle.open === 'number')
      ? data.candle
      : {
          open: Number(data.open ?? data.mid ?? data.bid) || 0,
          high: Number(data.high ?? data.mid ?? data.ask) || 0,
          low: Number(data.low ?? data.mid ?? data.bid) || 0,
          close: Number(data.close ?? data.mid ?? data.ask) || 0,
          timestamp: typeof data.timestamp === 'number' ? Math.floor(data.timestamp) : Math.floor(Date.now() / 1000),
        };
    
    if (candle && typeof candle.open === 'number' && typeof candle.high === 'number' && 
        typeof candle.low === 'number' && typeof candle.close === 'number' && 
        candle.timestamp && typeof candle.timestamp === 'number') {
      if (!candleCache[symbol]) {
        candleCache[symbol] = [];
      }
      
      const timestamp = Math.floor((candle.timestamp as number) / 60) * 60;
      
      const existingIndex = candleCache[symbol].findIndex(
        (c: any) => c.time === timestamp
      );
      
      const chartCandle = {
        time: timestamp as number,
        open: Number(candle.open) || 0,
        high: Number(candle.high) || 0,
        low: Number(candle.low) || 0,
        close: Number(candle.close) || 0,
      };
      
      if (chartCandle.open > 0 && chartCandle.high > 0 && chartCandle.low > 0 && chartCandle.close > 0) {
        if (existingIndex >= 0) {
          const prev = candleCache[symbol][existingIndex];
          candleCache[symbol][existingIndex] = {
            time: prev.time,
            open: prev.open || chartCandle.open,
            high: Math.max(prev.high, chartCandle.high),
            low: Math.min(prev.low, chartCandle.low),
            close: chartCandle.close,
          };
        } else {
          candleCache[symbol].push(chartCandle);
          if (candleCache[symbol].length > 500) {
            candleCache[symbol] = candleCache[symbol].slice(-500);
          }
        }
        
        candleCache[symbol].sort((a: any, b: any) => a.time - b.time);
      }
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
      {candles && candles.length > 0 ? (
        <PriceChart candles={candles} height={400} />
      ) : marketData && (marketData.bid > 0 || marketData.ask > 0) ? (
        // Show placeholder with price info while waiting for candles
        <div className="w-full h-96 rounded-lg border border-gray-700 bg-gray-800 flex flex-col items-center justify-center">
          <div className="text-gray-400 mb-4">Waiting for candle data...</div>
          <div className="text-sm text-gray-500">
            Current Price: {marketData.mid?.toFixed(5) || marketData.bid?.toFixed(5) || 'N/A'}
          </div>
          <div className="text-xs text-gray-600 mt-2">
            Candles will appear after 1-2 minutes of data collection
          </div>
        </div>
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