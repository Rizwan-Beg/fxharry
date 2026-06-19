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

  const lastDataLengthRef = useRef(0);
  const lastFirstTimeRef = useRef<any>(null);
  const lastTimeRef = useRef<any>(null);

  // Update chart data
  useEffect(() => {
    if (!seriesRef.current) return;

    if (!data || data.length === 0) {
      seriesRef.current.setData([]);
      lastDataLengthRef.current = 0;
      lastFirstTimeRef.current = null;
      lastTimeRef.current = null;
      return;
    }

    const firstTime = data[0].time;
    const lastPoint = data[data.length - 1];
    const isNewSeries = lastFirstTimeRef.current !== firstTime;
    
    // We can use update if we are either:
    // 1. Appending a single new point (time is newer than lastTimeRef)
    // 2. Updating the last point (time is equal to lastTimeRef)
    const isUpdateable = !isNewSeries && 
      (lastPoint.time === lastTimeRef.current || 
       (lastTimeRef.current !== null && lastPoint.time > lastTimeRef.current && data.length === lastDataLengthRef.current + 1));

    try {
      if (isUpdateable) {
        seriesRef.current.update(lastPoint);
      } else {
        seriesRef.current.setData(data);
      }
    } catch (e) {
      console.error("[PriceChart] Error updating chart series", e);
      // Fallback
      seriesRef.current.setData(data);
    }

    lastDataLengthRef.current = data.length;
    lastFirstTimeRef.current = firstTime;
    lastTimeRef.current = lastPoint.time;
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height }}
    />
  );
}
