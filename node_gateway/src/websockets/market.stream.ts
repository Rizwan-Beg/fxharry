import { ClientManager } from './client.manager';

let manager: ClientManager | null = null;

export function setClientManager(m: ClientManager) {
  manager = m;
}

export function broadcastMarketData(raw: any) {
  const normalized = normalize(raw);
  if (!manager) return;
  manager.broadcast(JSON.stringify(normalized));
}

function normalize(raw: any) {
  if (raw && raw.type === 'market_data' && raw.data) {
    return raw;
  }
  if (raw && raw.type === 'tick') {
    const symbol = raw.symbol;
    const tick = raw.tick || {};
    const micro = raw.micro || {};
    const candle = raw.candle || {};
    const bid = typeof tick.bid === 'number' ? tick.bid : 0;
    const ask = typeof tick.ask === 'number' ? tick.ask : 0;
    const mid = typeof tick.mid === 'number' ? tick.mid : (bid && ask ? (bid + ask) / 2 : 0);
    const spread = typeof tick.spread === 'number' ? tick.spread : (ask && bid ? ask - bid : 0);
    return {
      type: 'market_data',
      data: {
        symbol,
        bid,
        ask,
        mid,
        spread,
        micro,
        candle,
      },
    };
  }
  return raw;
}
