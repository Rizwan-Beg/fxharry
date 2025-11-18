// /src/components/PriceChart.tsx
import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, Time, CandlestickData } from "lightweight-charts";

interface Props {
  candles: CandlestickData<Time>[];
  height?: number;
}

export default function PriceChart({ candles, height = 350 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const lastCandleCountRef = useRef<number>(0);

  // Initialize chart
  useEffect(() => {
    if (!chartRef.current && containerRef.current) {
      chartRef.current = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height,
        layout: {
          background: { color: "#08121a" },
          textColor: "#dbeafe",
        },
        grid: {
          vertLines: { color: "rgba(255,255,255,0.03)" },
          horzLines: { color: "rgba(255,255,255,0.03)" },
        },
        crosshair: { mode: 1 },
        timeScale: { timeVisible: true, secondsVisible: false },
      });

      seriesRef.current = (chartRef.current as any).addCandlestickSeries({
        upColor: "#10b981",
        downColor: "#ef4444",
        borderUpColor: "#10b981",
        borderDownColor: "#ef4444",
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      });
    }

    const ro = new ResizeObserver(() => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, [height]);

  // Update chart data
  useEffect(() => {
    if (!seriesRef.current) return;

    if (candles.length === 0) {
      seriesRef.current.setData([]);
      lastCandleCountRef.current = 0;
      return;
    }

    // If this is the first load or candles count decreased, use setData
    if (lastCandleCountRef.current === 0 || candles.length < lastCandleCountRef.current) {
      seriesRef.current.setData(candles);
      lastCandleCountRef.current = candles.length;
      return;
    }

    // For incremental updates, update only the last candle
    if (candles.length > lastCandleCountRef.current) {
      const lastCandle = candles[candles.length - 1];
      seriesRef.current.update(lastCandle);
      lastCandleCountRef.current = candles.length;
    } else if (candles.length === lastCandleCountRef.current && candles.length > 0) {
      // Same count but data might have changed (candle update)
      const lastCandle = candles[candles.length - 1];
      seriesRef.current.update(lastCandle);
    }
  }, [candles]);

  return <div ref={containerRef} style={{ width: "100%", height }} />;
}
