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

  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      const list = listeners[msg.type] || [];
      list.forEach((fn) => fn(msg.data));
    } catch {}
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