import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, Time, CandlestickData } from "lightweight-charts";

// Local narrow type for charts that support adding a candlestick series
type ChartWithSeries = IChartApi & {
  addCandlestickSeries: (opts: Record<string, unknown>) => ISeriesApi<"Candlestick">;
};

interface Props {
  candles: CandlestickData<Time>[];
  height?: number;
}

export default function PriceChart({ candles, height = 320 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const lastCandleCountRef = useRef<number>(0);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const tryInit = () => {
      if (chartRef.current || !containerRef.current) return;
      const w = containerRef.current.clientWidth;
      if (w <= 0 || height <= 0) return;
      try {
        const chart = createChart(containerRef.current, {
          width: w,
          height,
          layout: { background: { color: "#08121a" }, textColor: "#dbeafe" },
          grid: { vertLines: { color: "rgba(255,255,255,0.03)" }, horzLines: { color: "rgba(255,255,255,0.03)" } },
          crosshair: { mode: 1 },
          timeScale: { timeVisible: true, secondsVisible: false },
        });

        const chartWithSeries = chart as unknown as ChartWithSeries;
        // Defensive: ensure chart exposes addCandlestickSeries before using it
        if (typeof chartWithSeries.addCandlestickSeries !== 'function') {
          console.error('[PriceChart] createChart returned unexpected object (no addCandlestickSeries). Skipping chart creation.');
          chartRef.current = null;
          seriesRef.current = null;
          return;
        }

        chartRef.current = chart;
        seriesRef.current = chartWithSeries.addCandlestickSeries({
          upColor: "#10b981",
          downColor: "#ef4444",
          borderUpColor: "#10b981",
          borderDownColor: "#ef4444",
          wickUpColor: "#10b981",
          wickDownColor: "#ef4444",
        });
      } catch (err) {
        console.error('[PriceChart] Error creating chart:', err);
        chartRef.current = null;
        seriesRef.current = null;
      }
    };

    tryInit();

    const ro = new ResizeObserver(() => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      if (chartRef.current) {
        chartRef.current.applyOptions({ width: w });
      } else {
        tryInit();
      }
    });
    ro.observe(el);
    return () => {
      ro.disconnect();
      if (chartRef.current) {
        try {
          chartRef.current.remove();
        } catch (e) {
          void e;
        }
      }
      chartRef.current = null;
      seriesRef.current = null;
      lastCandleCountRef.current = 0;
    };
  }, [height]);

  useEffect(() => {
    const series = seriesRef.current;
    if (!series) return;
    if (!Array.isArray(candles) || candles.length === 0) {
      series.setData([]);
      lastCandleCountRef.current = 0;
      return;
    }
    if (lastCandleCountRef.current === 0 || candles.length < lastCandleCountRef.current) {
      series.setData(candles);
      lastCandleCountRef.current = candles.length;
      return;
    }
    const last = candles[candles.length - 1];
    series.update(last);
    lastCandleCountRef.current = candles.length;
  }, [candles]);

  const containerStyle: React.CSSProperties = { width: "100%", height };
  // eslint-disable-next-line react/style-prop-object
  return <div ref={containerRef} style={containerStyle} />;
}
