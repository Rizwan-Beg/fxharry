import { useState, useEffect, useCallback } from 'react';
import { createWS, WS_URL } from '../services/ws';

export function useLiveFeed() {
  const [marketData, setMarketData] = useState<any>({});
  const [signals, setSignals] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState({
    ibkr: false,
    websocket: false,
    market_data: false,
  });

  const [selectedSymbol, setSelectedSymbol] = useState<string>('EURUSD');

  useEffect(() => {
    const { ws, on } = createWS(WS_URL);

    ws.onopen = () => {
      setConnectionStatus((prev) => ({ ...prev, websocket: true }));
    };

    ws.onclose = () => {
      setConnectionStatus((prev) => ({ ...prev, websocket: false }));
    };

    ws.onerror = () => {
      setConnectionStatus((prev) => ({ ...prev, websocket: false }));
    };

    on('market_data', (data: any) => {
      setMarketData((prev: any) => ({ ...prev, [data.symbol]: data }));
      setConnectionStatus((prev) => ({ ...prev, market_data: true, ibkr: true }));
    });

    on('connection_status', (data: any) => {
      setConnectionStatus((prev) => ({ ...prev, ibkr: !!data?.ibkr_connected }));
    });

    on('signal_update', (data: any) => {
      setSignals((prev) => Array.isArray(data) ? data : prev);
    });

    on('risk_alert', (data: any) => {
      setNotifications((prev) => [
        ...prev,
        {
          id: String(Date.now()),
          type: 'warning',
          title: data?.title || 'Risk Alert',
          message: data?.message || '',
          timestamp: new Date().toISOString(),
        },
      ]);
    });

    return () => {
      try { ws.close(); } catch {}
    };
  }, []);

  const subscribeToSymbol = useCallback((symbol: string) => {
    setSelectedSymbol(symbol);
  }, []);

  const unsubscribeFromSymbol = useCallback((_symbol: string) => {
  }, []);

  return {
    marketData,
    signals,
    notifications,
    connectionStatus,
    selectedSymbol,
    subscribeToSymbol,
    unsubscribeFromSymbol,
  };
}