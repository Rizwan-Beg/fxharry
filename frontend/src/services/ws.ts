function deriveWsUrl(): string {
  const env = (import.meta as any).env?.VITE_WS_URL as string | undefined;
  if (env) {
    if (env.startsWith('http')) {
      const base = env.replace(/^http/, 'ws').replace(/\/$/, '');
      return `${base}/ws`;
    }
    return env;
  }
  return 'ws://localhost:8080/ws';
}

export function createWS(url?: string) {
  const ws = new WebSocket(url || deriveWsUrl());
  const listeners: { [key: string]: ((data: any) => void)[] } = {};

  ws.onopen = () => {
    console.log('✅ WS connected to', url || deriveWsUrl());
  };

  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      
      // Handle welcome message
      if (msg.type === 'welcome') {
        console.log('WebSocket welcome received');
        return;
      }
      
      // Handle market_data messages (normalized by Node Gateway)
      if (msg.type === 'market_data' && msg.data) {
        const list = listeners['market_data'] || [];
        list.forEach((fn) => fn(msg.data));
      } else {
        // Handle other message types
        const list = listeners[msg.type] || [];
        list.forEach((fn) => fn(msg.data || msg));
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };

  return {
    on(type: string, fn: (data: any) => void) {
      listeners[type] = listeners[type] || [];
      listeners[type].push(fn);
    },
    ws,
  };
}

export const WS_URL = deriveWsUrl();