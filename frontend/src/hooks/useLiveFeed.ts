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
    candle?: Record<string, unknown>;
    candles?: Record<string, unknown>;
    micro?: Record<string, unknown>;
    timestamp?: number;
  };
};

export function useLiveFeed() {
  const [marketData, setMarketData] = useState<MarketDataBySymbol>({});
  const [signals, setSignals] = useState<unknown[]>([]);
  const [notifications, setNotifications] = useState<unknown[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("EURUSD");
  const [accountData, setAccountData] = useState<any>(null);
  const [tradeHistory, setTradeHistory] = useState<any[]>([]);
  const [strategies, setStrategies] = useState<any[]>([]);
  const [aiReasoning, setAiReasoning] = useState<any>(null);
  const [aiHistory, setAiHistory] = useState<any[]>([]);
  const [newsSentiment, setNewsSentiment] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [riskLimits, setRiskLimits] = useState<any>(null);
  const [backtestResults, setBacktestResults] = useState<any>(null);
  const [isBacktesting, setIsBacktesting] = useState<boolean>(false);
  const [strategyDiagnostics, setStrategyDiagnostics] = useState<any>(null);
  const [rejectedSignals, setRejectedSignals] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState({
    ibkr: false,
    websocket: false,
    market_data: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const connectingRef = useRef<boolean>(false);
  const reconnectTimerRef = useRef<number | null>(null);
  const messageCountRef = useRef<number>(0);

  const connect = useCallback(() => {
    if (connectingRef.current) return;

    const existing = wsRef.current;
    if (
      existing &&
      (existing.readyState === WebSocket.OPEN ||
        existing.readyState === WebSocket.CONNECTING)
    )
      return;

    connectingRef.current = true;

    const wsUrl = WS_URL;
    console.log(`[useLiveFeed] Connecting to WebSocket: ${wsUrl}`);

    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onopen = () => {
      connectingRef.current = false;
      setConnectionStatus((prev) => ({ ...prev, websocket: true }));
      console.log("[useLiveFeed] ✅ WebSocket connection established");
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

        // Light debug every 50th message
        if (messageCountRef.current % 50 === 0) {
          let dbgSymbol: string | undefined;
          let dbgHasCandle = false;
          let dbgBid: unknown;
          let dbgAsk: unknown;

          if (msg.type === "market_data" && msg.data) {
            const d: any = msg.data;
            if (d.symbol) {
              dbgSymbol = d.symbol;
              dbgHasCandle = !!d.candle;
              dbgBid = d.bid;
              dbgAsk = d.ask;
            } else if (typeof d === "object") {
              const firstKey = Object.keys(d)[0];
              const first = firstKey ? d[firstKey] : undefined;
              if (first) {
                dbgSymbol = first.symbol || firstKey;
                dbgHasCandle = !!first.candle;
                dbgBid = first.bid;
                dbgAsk = first.ask;
              }
            }
          }

          console.log(
            `[useLiveFeed] Received message #${messageCountRef.current}:`,
            {
              type: msg.type,
              symbol: dbgSymbol,
              hasCandle: dbgHasCandle,
              bid: dbgBid,
              ask: dbgAsk,
            }
          );
        }

        if (msg.type === "welcome") {
          console.log("[useLiveFeed] Received welcome message");
          return;
        }

        if (msg.type === "market_data" && msg.data) {
          const coerceNumber = (v: unknown): number | undefined => {
            if (v === null || v === undefined || v === "") return undefined;
            const n = Number(v);
            return Number.isFinite(n) ? n : undefined;
          };

          const buildSanitized = (raw: any, symbol: string) => {
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
              timestamp:
                coerceNumber(raw.timestamp) ||
                (raw.candle?.timestamp
                  ? coerceNumber(raw.candle.timestamp)
                  : undefined),
              candle: undefined,
              candles: undefined,
              micro: raw.micro || undefined,
            };

            // Single candle
            if (raw.candle && typeof raw.candle === "object") {
              const c = raw.candle;
              const ts =
                coerceNumber(c.timestamp) ||
                coerceNumber(c.time) ||
                undefined;
              sanitized.candle = {
                open: coerceNumber(c.open),
                high: coerceNumber(c.high),
                low: coerceNumber(c.low),
                close: coerceNumber(c.close),
                timestamp: ts,
              };
            }

            // Candles map (e.g. 1m/5m)
            if (raw.candles && typeof raw.candles === "object") {
              const out: Record<string, Record<string, unknown>> = {};
              for (const k of Object.keys(raw.candles)) {
                const v = raw.candles[k];
                if (v && typeof v === "object") {
                  const vRec = v as Record<string, unknown>;
                  const ts =
                    coerceNumber(vRec.timestamp) ||
                    coerceNumber(vRec.time) ||
                    undefined;
                  out[k] = {
                    open: coerceNumber(vRec.open),
                    high: coerceNumber(vRec.high),
                    low: coerceNumber(vRec.low),
                    close: coerceNumber(vRec.close),
                    timestamp: ts,
                  };
                }
              }
              sanitized.candles = out;
            }

            return sanitized;
          };

          const data = msg.data as any;
          const updates: Record<string, Record<string, unknown>> = {};

          // Case 1: single-object payload with .symbol
          if (data.symbol || data.bid || data.ask || data.mid) {
            const symbol = data.symbol || selectedSymbol || "EURUSD";
            updates[symbol] = buildSanitized(data, symbol);
          } else if (typeof data === "object") {
            // Case 2: map payload: { EURUSD: { ... }, GBPUSD: { ... } }
            for (const [symbol, value] of Object.entries(data)) {
              if (!value || typeof value !== "object") continue;
              updates[symbol] = buildSanitized(value as any, symbol);
            }
          }

          const symbols = Object.keys(updates);
          if (symbols.length === 0) {
            console.warn(
              "[useLiveFeed] market_data message without any usable symbols",
              msg.data
            );
            return;
          }

          setConnectionStatus((prev) => ({ ...prev, market_data: true }));

          setMarketData((prev) => {
            const updated: MarketDataBySymbol = { ...prev };
            for (const [symbol, sanitized] of Object.entries(updates)) {
              updated[symbol] = {
                ...(prev[symbol] || {}),
                ...sanitized,
              } as any;
            }

            if (messageCountRef.current % 100 === 0) {
              const firstSymbol = symbols[0];
              console.log(
                `[useLiveFeed] Updated market data for ${firstSymbol}:`,
                updated[firstSymbol]
              );
            }

            return updated;
          });

          return;
        } else if (msg.type === "connection_status") {
          const st = msg.data || msg.status;
          setConnectionStatus((prev) => ({
            ...prev,
            ibkr: !!(st?.ibkr_connected || st?.ibkr),
          }));
          console.log("[useLiveFeed] Connection status update:", st);
        } else if (msg.type === "signal_update") {
          const arr = Array.isArray(msg.data) ? msg.data : [];
          setSignals(arr);
          console.log("[useLiveFeed] Received signal update:", arr);
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
          console.warn("[useLiveFeed] Risk alert received");
        } else if (msg.type === "account_data") {
          setAccountData(msg.data);
          // console.log("[useLiveFeed] Received account data");
        } else if (msg.type === "trade_history") {
          if (Array.isArray(msg.data)) {
            setTradeHistory(msg.data);
            console.log("[useLiveFeed] Received trade history update");
          }
        } else if (msg.type === "ai_reasoning") {
          setAiReasoning(msg.data);
          setAiHistory((prev) => [msg.data, ...prev].slice(0, 10));
          console.log(
            `[useLiveFeed] 🧠 AI reasoning: ${msg.data?.recommendation} (${Math.round((msg.data?.confidence ?? 0) * 100)}%) — ${msg.data?.latency_ms}ms`
          );
        } else if (msg.type === "news_sentiment") {
          setNewsSentiment(msg.data);
          console.log(`[useLiveFeed] 📰 News Sentiment updated: ${msg.data?.sentiment}`);
        } else if (msg.type === "strategy_status") {
          if (Array.isArray(msg.data)) {
            setStrategies(msg.data);
          }
        } else if (msg.type === "risk_assessment") {
          setRiskAssessment(msg.data);
        } else if (msg.type === "risk_limits") {
          setRiskLimits(msg.data);
        } else if (msg.type === "backtest_result") {
          setIsBacktesting(false);
          setBacktestResults(msg.data);
          console.log("[useLiveFeed] Received backtest results");
        } else if (msg.type === "strategy_diagnostics") {
          setStrategyDiagnostics(msg.data);
        } else if (msg.type === "rejected_signal") {
          setRejectedSignals((prev) => [msg.data, ...prev].slice(0, 10));
          console.log("[useLiveFeed] Received rejected signal:", msg.data);
        } else {
          console.debug("[useLiveFeed] Received unknown message type:", msg.type);
        }
      } catch (err) {
        console.error(
          "[useLiveFeed] Error parsing WebSocket message:",
          err,
          ev.data
        );
      }
    };

    socket.onerror = (err) => {
      console.error("[useLiveFeed] WebSocket error:", err);
    };

    socket.onclose = () => {
      console.log("[useLiveFeed] WebSocket disconnected");
      setConnectionStatus((prev) => ({
        ...prev,
        websocket: false,
        market_data: false,
      }));
      if (reconnectTimerRef.current) return;
      console.log("[useLiveFeed] Attempting to reconnect in 3 seconds...");
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null;
        connect();
      }, 3000);
    };
  }, [selectedSymbol]);

  useEffect(() => {
    console.log("[useLiveFeed] Hook mounted, initiating connection...");
    connect();
    return () => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        try {
          ws.close();
          console.log("[useLiveFeed] WebSocket closed on unmount");
        } catch (err) {
          console.debug("[useLiveFeed] Error closing WebSocket:", err);
        }
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, []);

  const send = useCallback((type: string, payload: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      if (type === "backtest_command" && payload.command === "RUN_BACKTEST") {
        setIsBacktesting(true);
      }
      wsRef.current.send(JSON.stringify({ type, ...payload }));
    } else {
      console.warn("[useLiveFeed] WebSocket not connected, cannot send:", type);
    }
  }, []);

  const subscribeToSymbol = useCallback((symbol: string) => {
    console.log(`[useLiveFeed] Subscribing to symbol: ${symbol}`);
    setSelectedSymbol(symbol);
  }, []);

  const unsubscribeFromSymbol = useCallback(
    (symbol: string) => {
      console.log(`[useLiveFeed] Unsubscribing from symbol: ${symbol}`);
      if (selectedSymbol === symbol) setSelectedSymbol("EURUSD");
    },
    [selectedSymbol]
  );

  return {
    marketData,
    signals,
    notifications,
    connectionStatus,
    selectedSymbol,
    accountData,
    tradeHistory,
    strategies,
    aiReasoning,
    aiHistory,
    newsSentiment,
    riskAssessment,
    riskLimits,
    backtestResults,
    isBacktesting,
    strategyDiagnostics,
    rejectedSignals,
    subscribeToSymbol,
    unsubscribeFromSymbol,
    send,
  };
}
