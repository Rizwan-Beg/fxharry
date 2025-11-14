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
  // Handle Python tick format: { type: "tick", symbol, tick: {bid, ask, mid}, candle, micro }
  if (raw && raw.type === 'tick' && raw.symbol) {
    const symbol = raw.symbol;
    const tick = raw.tick || {};
    const micro = raw.micro || {};
    const candle = raw.candle || {};
    const bid = typeof tick.bid === 'number' && !isNaN(tick.bid) ? tick.bid : 0;
    const ask = typeof tick.ask === 'number' && !isNaN(tick.ask) ? tick.ask : 0;
    const mid = typeof tick.mid === 'number' && !isNaN(tick.mid) 
      ? tick.mid 
      : (bid > 0 && ask > 0 ? (bid + ask) / 2 : 0);
    const spread = typeof tick.spread === 'number' && !isNaN(tick.spread)
      ? tick.spread
      : (bid > 0 && ask > 0 ? ask - bid : 0);
    
    // Extract OHLC from candle if available
    const open = candle?.open || mid;
    const high = candle?.high || mid;
    const low = candle?.low || mid;
    const close = candle?.close || mid;
    
    return {
      type: 'market_data',
      data: {
        symbol,
        bid,
        ask,
        mid,
        spread,
        open,
        high,
        low,
        close,
        micro,
        candle,
        timestamp: tick.timestamp || Date.now() / 1000,
      },
    };
  }
  
  // Handle legacy market_data format
  if (raw && raw.type === 'market_data' && raw.data) {
    return raw;
  }
  
  // Fallback: return as-is
  return raw;
}
