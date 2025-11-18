import React, { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, Time } from "lightweight-charts";
console.log("[DEBUG] createChart =", createChart);
console.log("[DEBUG] typeof createChart =", typeof createChart);


interface Props {
  data: { time: Time; value: number }[];
  height?: number;
}

export default function PriceChart({ data, height = 300 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);

  // Initialize chart
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const width = el.clientWidth || 400;

    const chart = createChart(el, {
      width,
      height,
      layout: {
        background: { color: "#08121a" },
        textColor: "#dbeafe",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.08)" },
        horzLines: { color: "rgba(255,255,255,0.08)" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
     
 
    }
  );
      console.log("[DEBUG] chart returned =", chart);
      console.log("[DEBUG] chart keys =", Object.keys(chart));
      console.log("CHART METHODS:", Object.keys(chart));


    const lineSeries = chart.addLineSeries({
      color: "#4ade80",
      lineWidth: 2,
    });

    chartRef.current = chart;
    seriesRef.current = lineSeries;

    const ro = new ResizeObserver(() => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        });
      }
    });

    ro.observe(el);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [height]);

  // Update chart data
  useEffect(() => {
    if (!seriesRef.current) return;

    if (!data || data.length === 0) {
      seriesRef.current.setData([]);
      return;
    }

    if (data.length === 1) {
      seriesRef.current.setData(data);
      return;
    }

    seriesRef.current.update(data[data.length - 1]);
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height }}
    />
  );
}
