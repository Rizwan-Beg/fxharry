export function createWS(url: string) {
  const ws = new WebSocket(url);
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