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
  try {
    const keys = normalized && normalized.data ? Object.keys(normalized.data) : [];
    console.log(`[market.stream] Broadcasting market_data for: ${keys.join(',')}`);
  } catch (e) {}
  manager.broadcast(JSON.stringify(normalized));
  try {
    manager.broadcast(JSON.stringify({ type: 'connection_status', data: { ibkr_connected: true } }));
  } catch {}
}

function normalize(raw: any) {
  // Handle Python tick format: { type: "tick", symbol, tick: {bid, ask, mid}, candle, candles, micro }
  if (raw && raw.type === 'tick' && raw.symbol) {
    const symbol = raw.symbol;
    const tick = raw.tick || {};
    const micro = raw.micro || {};
    
    // Extract latest candle from various possible formats
    let candle: any = null;
    // Try selecting from raw.candles or raw.candle
    if (raw.candles && raw.candles['1m']) {
      candle = raw.candles['1m'];
    } else if (raw.candle && typeof raw.candle.open === 'number') {
      candle = raw.candle;
    } else if (raw.candles) {
      // Fallback to any timeframe
      const tfs = Object.keys(raw.candles || {});
      if (tfs.length > 0) {
        const tf = tfs[0];
        // If buckets keyed by timestamp
        const buckets = raw.candles[tf];
        if (buckets && typeof buckets === 'object') {
          const keys = Object.keys(buckets).map((k) => Number(k)).filter((n) => !Number.isNaN(n));
          if (keys.length > 0) {
            const latest = String(Math.max(...keys));
            candle = buckets[latest] || buckets[Object.keys(buckets)[0]];
          }
        }
      }
    }
    
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
    const candleTimestamp = candle?.timestamp || Math.floor(Date.now() / 1000);

    // Include all candles for multi-timeframe support
    const allCandles = raw.candles || {};
    if (candle && !allCandles['1m']) {
      allCandles['1m'] = candle;
    }

    return {
      type: 'market_data',
      data: {
        [symbol]: {
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
          candle: {
            open,
            high,
            low,
            close,
            timestamp: candleTimestamp,
          },
          candles: allCandles,
          timestamp: tick.timestamp || Math.floor(Date.now() / 1000),
        },
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
    
    let candle: any = null;
    if (d.candle && typeof d.candle.open === 'number') {
      candle = d.candle;
    }
    
    return {
      type: 'market_data',
      data: {
        [d.symbol]: {
          symbol: d.symbol,
          bid,
          ask,
          mid,
          spread,
          open: candle?.open || mid,
          high: candle?.high || mid,
          low: candle?.low || mid,
          close: candle?.close || mid,
          micro: d.micro,
          candle: candle || { open: mid, high: mid, low: mid, close: mid, timestamp: Math.floor(Date.now() / 1000) },
          candles: d.candles || {},
          timestamp: d.timestamp || Math.floor(Date.now() / 1000),
        },
      },
    };
  }
  
  // Fallback: return as-is
  return raw;
}
