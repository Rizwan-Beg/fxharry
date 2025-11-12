import { useState, useEffect, useCallback } from 'react';

export function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [marketData, setMarketData] = useState<any>({});
  const [signals, setSignals] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState({
    ibkr: false,
    websocket: false,
    market_data: false
  });

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus(prev => ({ ...prev, websocket: true }));
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus(prev => ({ ...prev, websocket: false }));
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'market_data':
              setMarketData(data.data);
              setSignals(data.signals || []);
              setConnectionStatus(prev => ({ ...prev, market_data: true }));
              break;
              
            case 'risk_alert':
              setNotifications(prev => [...prev, {
                id: `risk-${Date.now()}`,
                type: 'warning',
                title: 'Risk Alert',
                message: 'Portfolio risk level is elevated',
                timestamp: new Date().toISOString()
              }]);
              break;
              
            case 'trade_executed':
              setNotifications(prev => [...prev, {
                id: `trade-${Date.now()}`,
                type: 'success',
                title: 'Trade Executed',
                message: `${data.action} ${data.quantity} ${data.symbol}`,
                timestamp: new Date().toISOString()
              }]);
              break;
              
            case 'connection_status':
              setConnectionStatus(data.status);
              break;
              
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      setSocket(ws);
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }, [url]);

  useEffect(() => {
    connect();
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [connect]);

  // Generate some mock data for demonstration
  useEffect(() => {
    const interval = setInterval(() => {
      // Mock market data updates
      const symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'USDCAD'];
      const mockMarketData: any = {};
      
      symbols.forEach(symbol => {
        const baseRates = {
          'EURUSD': 1.0850,
          'GBPUSD': 1.2650,
          'XAUUSD': 2020.50,
          'USDJPY': 149.20,
          'USDCAD': 1.3520
        };
        
        const baseRate = baseRates[symbol as keyof typeof baseRates];
        const change = (Math.random() - 0.5) * 0.002 * baseRate;
        const price = baseRate + change;
        
        mockMarketData[symbol] = {
          symbol,
          close: price,
          bid: price - 0.0002,
          ask: price + 0.0002,
          high: price + Math.abs(change),
          low: price - Math.abs(change),
          open: baseRate,
          change,
          change_percent: (change / baseRate) * 100,
          volume: Math.floor(Math.random() * 1000000) + 100000,
          spread: 0.0004,
          timestamp: new Date().toISOString()
        };
      });
      
      setMarketData(mockMarketData);
      setConnectionStatus(prev => ({ ...prev, market_data: true, ibkr: true }));
      
      // Occasionally generate mock signals
      if (Math.random() < 0.1) { // 10% chance
        const randomSymbol = symbols[Math.floor(Math.random() * symbols.length)];
        const newSignal = {
          symbol: randomSymbol,
          signal: Math.random() > 0.5 ? 'BUY' : 'SELL',
          confidence: 0.5 + Math.random() * 0.4, // 0.5 to 0.9
          strategy_id: Math.floor(Math.random() * 3) + 1,
          timestamp: new Date().toISOString()
        };
        
        setSignals(prev => [newSignal, ...prev.slice(0, 9)]); // Keep last 10 signals
      }
    }, 2000); // Update every 2 seconds
    
    return () => clearInterval(interval);
  }, []);

  return {
    socket,
    marketData,
    signals,
    notifications,
    connectionStatus
  };
}