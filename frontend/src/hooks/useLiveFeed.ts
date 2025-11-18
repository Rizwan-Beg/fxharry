import { useState, useEffect, useCallback, useRef } from "react";
import { WS_URL } from "../services/ws";

type MarketDataBySymbol = {
  [symbol: string]: {
    symbol: string;
    bid: number;
    ask: number;
    mid: number;
    spread: number;
    open?: number;
    high?: number;
    low?: number;
    close?: number;
    candle?: any;
    micro?: any;
    timestamp?: number;
  };
};

export function useLiveFeed() {
  const [marketData, setMarketData] = useState<MarketDataBySymbol>({});
  const [signals, setSignals] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("EURUSD");
  const [connectionStatus, setConnectionStatus] = useState({ ibkr: false, websocket: false, market_data: false });

  const wsRef = useRef<WebSocket | null>(null);
  const connectingRef = useRef<boolean>(false);
  const reconnectTimerRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (connectingRef.current) return;
    const existing = wsRef.current;
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) return;
    connectingRef.current = true;
    const socket = new WebSocket(WS_URL);
    wsRef.current = socket;

    socket.onopen = () => {
      connectingRef.current = false;
      setConnectionStatus((prev) => ({ ...prev, websocket: true }));
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    socket.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "welcome") return;
        if (msg.type === "market_data" && msg.data) {
          const d = msg.data;
          const symbol = d.symbol;
          if (!symbol) return;
          setConnectionStatus((prev) => ({ ...prev, market_data: true }));
          setMarketData((prev) => ({ ...prev, [symbol]: { ...(prev[symbol] || {}), ...d } }));
        } else if (msg.type === "connection_status") {
          const st = msg.data || msg.status;
          setConnectionStatus((prev) => ({ ...prev, ibkr: !!(st?.ibkr_connected || st?.ibkr) }));
        } else if (msg.type === "signal_update") {
          const arr = Array.isArray(msg.data) ? msg.data : [];
          setSignals(arr);
        } else if (msg.type === "risk_alert") {
          setNotifications((prev) => [
            ...prev,
            {
              id: String(Date.now()),
              type: "warning",
              title: "Risk Alert",
              message: "Portfolio risk level is elevated",
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      } catch {}
    };

    socket.onerror = () => {};

    socket.onclose = () => {
      setConnectionStatus((prev) => ({ ...prev, websocket: false, market_data: false }));
      if (reconnectTimerRef.current) return;
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null;
        connect();
      }, 3000);
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    connect();
    return () => {
      isMounted = false;
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        try {
          ws.close();
        } catch {}
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, [connect]);

  const subscribeToSymbol = useCallback((symbol: string) => {
    setSelectedSymbol(symbol);
  }, []);

  const unsubscribeFromSymbol = useCallback((symbol: string) => {
    if (selectedSymbol === symbol) setSelectedSymbol("EURUSD");
  }, [selectedSymbol]);

  return { marketData, signals, notifications, connectionStatus, selectedSymbol, subscribeToSymbol, unsubscribeFromSymbol };
}
