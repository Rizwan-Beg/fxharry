import React, { useEffect, useRef, useMemo } from 'react';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';

interface TradingChartProps {
  symbol: string;
  marketData: any;
  signals: any[];
}

export function TradingChart({ symbol, marketData, signals }: TradingChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Generate sample price data for demonstration
  const priceData = useMemo(() => {
    const basePrice = marketData?.close || 1.0850;
    const data = [];
    
    for (let i = 0; i < 100; i++) {
      const noise = (Math.random() - 0.5) * 0.002;
      const trend = Math.sin(i * 0.1) * 0.001;
      const price = basePrice + trend + noise;
      
      data.push({
        time: Date.now() - (100 - i) * 60000, // 1 minute intervals
        price: price,
        volume: Math.random() * 100 + 50
      });
    }
    
    return data;
  }, [marketData, symbol]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    
    // Vertical grid lines
    for (let i = 0; i < canvas.width; i += 50) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }
    
    // Horizontal grid lines
    for (let i = 0; i < canvas.height; i += 30) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }

    // Draw price line
    if (priceData.length > 1) {
      const minPrice = Math.min(...priceData.map(d => d.price));
      const maxPrice = Math.max(...priceData.map(d => d.price));
      const priceRange = maxPrice - minPrice || 0.001;
      
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      priceData.forEach((point, index) => {
        const x = (index / (priceData.length - 1)) * canvas.width;
        const y = canvas.height - ((point.price - minPrice) / priceRange) * canvas.height;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();

      // Draw AI signals
      signals?.forEach((signal) => {
        const signalIndex = Math.floor(Math.random() * priceData.length);
        const x = (signalIndex / (priceData.length - 1)) * canvas.width;
        const y = canvas.height - ((priceData[signalIndex].price - minPrice) / priceRange) * canvas.height;
        
        ctx.fillStyle = signal.signal === 'BUY' ? '#10b981' : '#ef4444';
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fill();
        
        // Signal label
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(
          signal.signal, 
          x, 
          y - 15
        );
      });
    }

    // Draw current price info
    if (marketData) {
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 16px Inter';
      ctx.textAlign = 'left';
      ctx.fillText(`${symbol}: ${marketData.close?.toFixed(5)}`, 10, 25);
      
      const change = marketData.change || 0;
      ctx.fillStyle = change >= 0 ? '#10b981' : '#ef4444';
      ctx.fillText(
        `${change >= 0 ? '+' : ''}${change.toFixed(5)} (${((change / marketData.close) * 100).toFixed(2)}%)`,
        10,
        50
      );
    }

  }, [priceData, signals, marketData, symbol]);

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
                <span className="text-white">{marketData.bid?.toFixed(5)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Ask:</span>
                <span className="text-white">{marketData.ask?.toFixed(5)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-400">Spread:</span>
                <span className="text-white">{marketData.spread?.toFixed(1)} pips</span>
              </div>
            </>
          )}
        </div>
      </div>
      
      <canvas
        ref={canvasRef}
        className="w-full h-96 rounded-lg border border-gray-700"
        style={{ imageRendering: 'pixelated' }}
      />
      
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
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Buy Signals</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Sell Signals</span>
          </div>
        </div>
      </div>
    </div>
  );
}