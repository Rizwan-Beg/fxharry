/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useMemo } from "react";
import { Activity } from "lucide-react";
import PriceChart from "./PriceChart";

interface TradingChartProps {
  symbol: string;
  marketData: any;
  signals: any[];
}

// Simple price history cache
const priceCache: { [symbol: string]: any[] } = {};

export function TradingChart({ symbol, marketData, signals }: TradingChartProps) {
  // Build real-time line chart data
  const lineData = useMemo(() => {
    if (!marketData) return [];

    if (!priceCache[symbol]) priceCache[symbol] = [];

    const timestampRaw = marketData.timestamp || Math.floor(Date.now() / 1000);

    const timestamp =
      timestampRaw > 1000000000000
        ? Math.floor(timestampRaw / 1000)
        : Math.floor(timestampRaw);

    const price = Number(marketData.mid || marketData.bid || marketData.ask);

    if (price > 0) {
      const lastIdx = priceCache[symbol].length - 1;
      if (lastIdx >= 0 && priceCache[symbol][lastIdx].time === timestamp) {
        // Update the existing point to avoid duplicates at same timestamp
        priceCache[symbol][lastIdx].value = price;
      } else {
        // Only push if time is strictly greater (preventing out-of-order)
        if (lastIdx < 0 || timestamp > priceCache[symbol][lastIdx].time) {
          priceCache[symbol].push({
            time: timestamp,
            value: price,
          });
        } else {
          console.warn(`[TradingChart] Ignored out-of-order tick for ${symbol}: timestamp=${timestamp}, last=${priceCache[symbol][lastIdx].time}`);
        }
      }
    }

    // Keep memory small
    if (priceCache[symbol].length > 1500) {
      priceCache[symbol] = priceCache[symbol].slice(-1500);
    }

    return [...priceCache[symbol]];
  }, [marketData, symbol]);

  const bid = Number(marketData?.bid || 0);
  const ask = Number(marketData?.ask || 0);
  const spread = ask > 0 && bid > 0 ? ask - bid : 0;
  const mid = Number(marketData?.mid || 0);

  return (
    <div className="relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-400" />
          <h3 className="text-lg font-semibold">{symbol} Price</h3>
        </div>

        {marketData && (
          <div className="flex items-center space-x-4 text-sm">
            <span className="text-gray-400">Bid: <span className="text-white">{bid.toFixed(5)}</span></span>
            <span className="text-gray-400">Ask: <span className="text-white">{ask.toFixed(5)}</span></span>
            <span className="text-gray-400">Mid: <span className="text-white">{mid.toFixed(5)}</span></span>
            <span className="text-gray-400">Spread: <span className="text-white">{spread.toFixed(5)}</span></span>
          </div>
        )}
      </div>

      {/* REAL-TIME LINE CHART */}
      <PriceChart data={lineData} height={400} />

      {/* Signals / legend */}
      <div className="flex justify-between items-center mt-4">
        <div className="flex space-x-2 text-sm">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span>Price</span>
          </div>
        </div>

        {signals && signals.length > 0 && (
          <div className="flex space-x-2 text-sm">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Buy Signals</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span>Sell Signals</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}