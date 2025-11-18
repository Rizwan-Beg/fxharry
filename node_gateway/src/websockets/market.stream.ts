import { ClientManager } from './client.manager';

let manager: ClientManager | null = null;

export function setClientManager(m: ClientManager) {
  manager = m;
}

export function broadcastMarketData(raw: any) {
  const normalized = normalize(raw);
  if (!manager) {
    console.error('ClientManager not set - cannot broadcast');
    return;
  }
  const clientCount = manager.getClientCount();
  if (clientCount === 0) {
    console.warn('No clients connected - data not broadcast');
    return;
  }
  manager.broadcast(JSON.stringify(normalized));
  try {
    manager.broadcast(JSON.stringify({ type: 'connection_status', data: { ibkr_connected: true } }));
  } catch {}
}

function normalize(raw: any) {
  // Handle Python tick format: { type: "tick", symbol, tick: {bid, ask, mid}, candle, micro }
  if (raw && raw.type === 'tick' && raw.symbol) {
    const symbol = raw.symbol;
    const tick = raw.tick || {};
    const micro = raw.micro || {};
    const candle = extractLatestCandle(raw.candle || {});
    const bid = typeof tick.bid === 'number' && !isNaN(tick.bid) ? tick.bid : 0;
    const ask = typeof tick.ask === 'number' && !isNaN(tick.ask) ? tick.ask : 0;
    const mid = typeof tick.mid === 'number' && !isNaN(tick.mid) 
      ? tick.mid 
      : (bid > 0 && ask > 0 ? (bid + ask) / 2 : 0);
    const spread = typeof tick.spread === 'number' && !isNaN(tick.spread)
      ? tick.spread
      : (bid > 0 && ask > 0 ? ask - bid : 0);
    
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
    const d = raw.data;
    const bid = typeof d.bid === 'number' && !isNaN(d.bid) ? d.bid : 0;
    const ask = typeof d.ask === 'number' && !isNaN(d.ask) ? d.ask : 0;
    const mid = typeof d.mid === 'number' && !isNaN(d.mid) ? d.mid : (bid > 0 && ask > 0 ? (bid + ask) / 2 : 0);
    const spread = typeof d.spread === 'number' && !isNaN(d.spread) ? d.spread : (bid > 0 && ask > 0 ? ask - bid : 0);
    const candle = extractLatestCandle(d.candle);
    return {
      type: 'market_data',
      data: {
        symbol: d.symbol,
        bid,
        ask,
        mid,
        spread,
        micro: d.micro,
        candle,
        timestamp: d.timestamp || Date.now() / 1000,
      },
    };
  }
  
  // Fallback: return as-is
  return raw;
}

function extractLatestCandle(candles: any): any | undefined {
  if (!candles || typeof candles !== 'object') return undefined;
  if (
    typeof candles.open === 'number' &&
    typeof candles.high === 'number' &&
    typeof candles.low === 'number' &&
    typeof candles.close === 'number' &&
    typeof candles.timestamp === 'number'
  ) {
    return candles;
  }
  const tf = candles['1m'] ? '1m' : Object.keys(candles)[0];
  if (!tf) return undefined;
  const buckets = candles[tf];
  if (!buckets || typeof buckets !== 'object') return undefined;
  const keys = Object.keys(buckets).map((k) => Number(k)).filter((n) => !Number.isNaN(n));
  if (keys.length === 0) return undefined;
  const latestTs = Math.max(...keys);
  const c = buckets[String(latestTs)] || buckets[latestTs];
  if (!c) return undefined;
  return {
    open: Number(c.open) || 0,
    high: Number(c.high) || 0,
    low: Number(c.low) || 0,
    close: Number(c.close) || 0,
    timestamp: Number(c.timestamp) || latestTs,
    timeframe: tf,
  };
}
