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
  candle?: Record<string, unknown> | undefined;
  micro?: Record<string, unknown> | undefined;
    timestamp?: number;
  };
};

export function useLiveFeed() {
  const [marketData, setMarketData] = useState<MarketDataBySymbol>({});
  const [signals, setSignals] = useState<unknown[]>([]);
  const [notifications, setNotifications] = useState<unknown[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("EURUSD");
  const [connectionStatus, setConnectionStatus] = useState({ ibkr: false, websocket: false, market_data: false });

  const wsRef = useRef<WebSocket | null>(null);
  const connectingRef = useRef<boolean>(false);
  const reconnectTimerRef = useRef<number | null>(null);
  const messageCountRef = useRef<number>(0);

  const connect = useCallback(() => {
    if (connectingRef.current) return;
    const existing = wsRef.current;
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) return;
    connectingRef.current = true;
    
    const wsUrl = WS_URL;
    console.log(`[useLiveFeed] Connecting to WebSocket: ${wsUrl}`);
    
    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onopen = () => {
      connectingRef.current = false;
      setConnectionStatus((prev) => ({ ...prev, websocket: true }));
      console.log('[useLiveFeed] ✅ WebSocket connection established');
      messageCountRef.current = 0;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    socket.onmessage = (ev) => {
      try {
        messageCountRef.current++;
        const msg = JSON.parse(ev.data);
        
        // Log every 50th message to avoid console spam
        if (messageCountRef.current % 50 === 0) {
          console.log(`[useLiveFeed] Received message #${messageCountRef.current}:`, {
            type: msg.type,
            symbol: msg.data?.symbol,
            hasCandle: !!msg.data?.candle,
            bid: msg.data?.bid,
            ask: msg.data?.ask,
          });
        }
        
        if (msg.type === "welcome") {
          console.log('[useLiveFeed] Received welcome message');
          return;
        }
        
        if (msg.type === "market_data" && msg.data) {
          // Sanitize and coerce numeric fields to avoid runtime errors in components
          const raw = msg.data;
          const symbol = raw.symbol;
          if (!symbol) {
            console.warn('[useLiveFeed] Received market_data without symbol');
            return;
          }

          const coerceNumber = (v: unknown) => {
            if (v === null || v === undefined || v === '') return undefined;
            const n = Number(v);
            return Number.isFinite(n) ? n : undefined;
          };

          const sanitized: Record<string, unknown> = {
            symbol,
            bid: coerceNumber(raw.bid),
            ask: coerceNumber(raw.ask),
            mid: coerceNumber(raw.mid),
            spread: coerceNumber(raw.spread),
            open: coerceNumber(raw.open),
            high: coerceNumber(raw.high),
            low: coerceNumber(raw.low),
            close: coerceNumber(raw.close),
            timestamp: coerceNumber(raw.timestamp) || (raw.candle?.timestamp ? coerceNumber(raw.candle.timestamp) : undefined),
            candle: undefined,
            candles: undefined,
            micro: raw.micro || raw.micro || undefined,
          };

          // Normalize single candle if present
          if (raw.candle && typeof raw.candle === 'object') {
            const c = raw.candle;
            const ts = coerceNumber(c.timestamp) || coerceNumber(c.time) || undefined;
            sanitized.candle = {
              open: coerceNumber(c.open),
              high: coerceNumber(c.high),
              low: coerceNumber(c.low),
              close: coerceNumber(c.close),
              timestamp: ts,
            };
          }

          // Normalize candles map if present (e.g., candles['1m'])
          if (raw.candles && typeof raw.candles === 'object') {
            sanitized.candles = {} as Record<string, unknown>;
            for (const k of Object.keys(raw.candles)) {
              const v = raw.candles[k];
              if (v && typeof v === 'object') {
                const vRec = v as Record<string, unknown>;
                const ts = coerceNumber(vRec.timestamp) || coerceNumber(vRec.time) || undefined;
                (sanitized.candles as Record<string, Record<string, unknown>>)[k] = {
                  open: coerceNumber(vRec.open),
                  high: coerceNumber(vRec.high),
                  low: coerceNumber(vRec.low),
                  close: coerceNumber(vRec.close),
                  timestamp: ts,
                };
              }
            }
          }

          setConnectionStatus((prev) => ({ ...prev, market_data: true }));
          setMarketData((prev) => {
            const updated = { ...prev, [symbol]: { ...(prev[symbol] || {}), ...sanitized } };
            if (messageCountRef.current % 100 === 0) {
              const symbolData = updated[symbol as keyof typeof updated];
              console.log(`[useLiveFeed] Updated market data for ${symbol}:`, symbolData);
            }
            return updated;
          });
        } else if (msg.type === "connection_status") {
          const st = msg.data || msg.status;
          setConnectionStatus((prev) => ({ ...prev, ibkr: !!(st?.ibkr_connected || st?.ibkr) }));
          console.log('[useLiveFeed] Connection status update:', st);
        } else if (msg.type === "signal_update") {
          const arr = Array.isArray(msg.data) ? msg.data : [];
          setSignals(arr);
          console.log('[useLiveFeed] Received signal update:', arr);
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
          console.warn('[useLiveFeed] Risk alert received');
        } else {
          console.debug('[useLiveFeed] Received unknown message type:', msg.type);
        }
      } catch (err) {
        console.error('[useLiveFeed] Error parsing WebSocket message:', err, ev.data);
      }
    };

    socket.onerror = (err) => {
      console.error('[useLiveFeed] WebSocket error:', err);
    };

    socket.onclose = () => {
      console.log('[useLiveFeed] WebSocket disconnected');
      setConnectionStatus((prev) => ({ ...prev, websocket: false, market_data: false }));
      if (reconnectTimerRef.current) return;
      console.log('[useLiveFeed] Attempting to reconnect in 3 seconds...');
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null;
        connect();
      }, 3000);
    };
  }, []);

  useEffect(() => {
    console.log('[useLiveFeed] Hook mounted, initiating connection...');
    connect();
    return () => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        try {
          ws.close();
          console.log('[useLiveFeed] WebSocket closed on unmount');
        } catch (err) {
          console.debug('[useLiveFeed] Error closing WebSocket:', err);
        }
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, [connect]);

  const subscribeToSymbol = useCallback((symbol: string) => {
    console.log(`[useLiveFeed] Subscribing to symbol: ${symbol}`);
    setSelectedSymbol(symbol);
  }, []);

  const unsubscribeFromSymbol = useCallback((symbol: string) => {
    console.log(`[useLiveFeed] Unsubscribing from symbol: ${symbol}`);
    if (selectedSymbol === symbol) setSelectedSymbol("EURUSD");
  }, [selectedSymbol]);

  return { marketData, signals, notifications, connectionStatus, selectedSymbol, subscribeToSymbol, unsubscribeFromSymbol };
}
