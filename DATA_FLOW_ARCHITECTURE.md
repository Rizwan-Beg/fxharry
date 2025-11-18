# Data Flow Architecture - Quick Reference

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      IBKR STREAMING (Python)                            │
│  ibkr_streaming/run.py → ibkr_streaming/tick_stream.py                  │
│                                                                         │
│  Receives: Real-time tick data from Interactive Brokers API             │
│  Processes: Bid/Ask/Mid calculations, Candle aggregation                │
│  Sends: WebSocket message to Node Gateway                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    WebSocket: ws://localhost:8080/ws
                    Message Format:
                    {
                      "type": "tick",
                      "symbol": "EURUSD",
                      "tick": {
                        "bid": 1.0847,
                        "ask": 1.0849,
                        "mid": 1.0848,
                        "spread": 0.0002,
                        "timestamp": 1700000000.123
                      },
                      "candle": { /* 1m candle */ },
                      "candles": { /* all timeframes */ },
                      "micro": { /* microstructure data */ }
                    }
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    NODE GATEWAY (TypeScript/Express)                     │
│  node_gateway/src/index.ts → websockets/market.stream.ts                │
│  websockets/client.manager.ts                                           │
│                                                                         │
│  Receives: tick messages from Python                                    │
│  Normalizes: Converts to market_data format                             │
│  Broadcasts: To all connected browser WebSocket clients                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    WebSocket: ws://localhost:8080/ws
                    Message Format:
                    {
                      "type": "market_data",
                      "data": {
                        "symbol": "EURUSD",
                        "bid": 1.0847,
                        "ask": 1.0849,
                        "mid": 1.0848,
                        "spread": 0.0002,
                        "open": 1.0845,
                        "high": 1.0850,
                        "low": 1.0840,
                        "close": 1.0848,
                        "candle": { /* normalized */ },
                        "candles": { /* all timeframes */ },
                        "timestamp": 1700000000.123
                      }
                    }
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND (TypeScript)                        │
│                                                                         │
│  App.tsx                                                               │
│    └── hooks/useLiveFeed.ts (handles WebSocket connection)             │
│        ├── Connects to Node Gateway WebSocket                          │
│        ├── Updates state with received market_data                     │
│        └── Provides marketData to components                           │
│                                                                         │
│  TradingDashboard.tsx                                                  │
│    └── TradingChart.tsx (converts data to candles)                     │
│        ├── Receives marketData prop                                    │
│        ├── Extracts/builds candles from tick data                      │
│        ├── Maintains candle cache (max 500 candles)                    │
│        └── Passes to PriceChart                                        │
│            └── PriceChart.tsx (lightweight-charts)                     │
│                ├── Receives candle array                               │
│                ├── Creates candlestick series                          │
│                └── Renders chart UI                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                            BROWSER DISPLAY
                        ✅ Real-time candlestick chart
```

---

## 📊 Data Transformation Pipeline

### Python Side: IBKR Tick → Candle
```
IBKR API Tick
    ↓
tick_stream.py: Extract bid/ask/mid
    ↓
candle_engine.py: Aggregate by timeframe (1m, 5m, 15m, 1h, 4h)
    ↓
run.py: Package into WebSocket message
    ↓
ws_push.py: Send to Node Gateway
```

### Node.js Side: Tick → Market Data
```
Receive { type: "tick", ... }
    ↓
market.stream.ts normalize():
    - Extract candle from raw.candles['1m'] or raw.candle
    - Validate numeric values
    - Calculate open/high/low/close from fallback
    - Include all timeframes
    ↓
Transform to { type: "market_data", data: { ... } }
    ↓
client.manager.ts broadcast():
    - Send to all connected WebSocket clients
```

### React Side: Market Data → Chart
```
useLiveFeed receives message
    ↓
Update state: marketData[symbol] = newData
    ↓
TradingDashboard passes marketData prop
    ↓
TradingChart:
    - useMemo extracts candle
    - Maintains candleCache[symbol]
    - Converts to lightweight-charts format
    - Returns candle array
    ↓
PriceChart:
    - Receives candle array
    - On first data: series.setData(candles)
    - On updates: series.update(lastCandle)
    ↓
✅ Chart displays candlesticks
```

---

## 🔑 Key Data Structures

### Market Data State (Frontend)
```typescript
marketData: {
  "EURUSD": {
    symbol: "EURUSD",
    bid: 1.0847,
    ask: 1.0849,
    mid: 1.0848,
    spread: 0.0002,
    open: 1.0845,           // From candle
    high: 1.0850,           // From candle
    low: 1.0840,            // From candle
    close: 1.0848,          // From candle
    candle: {
      open: 1.0845,
      high: 1.0850,
      low: 1.0840,
      close: 1.0848,
      timestamp: 1700000000 (Unix seconds)
    },
    candles: {
      "1m": { open, high, low, close, timestamp },
      "5m": { open, high, low, close, timestamp },
      "15m": { open, high, low, close, timestamp },
      "1h": { open, high, low, close, timestamp },
      "4h": { open, high, low, close, timestamp }
    },
    timestamp: 1700000000
  },
  "GBPUSD": { ... },
  ...
}
```

### Candle Cache (Frontend)
```typescript
candleCache: {
  "EURUSD": [
    { time: 1700000000, open: 1.0840, high: 1.0850, low: 1.0835, close: 1.0845 },
    { time: 1700000060, open: 1.0845, high: 1.0855, low: 1.0843, close: 1.0850 },
    { time: 1700000120, open: 1.0850, high: 1.0860, low: 1.0848, close: 1.0858 },
    ...
  ]
  // Max 500 candles per symbol, older ones removed
}
```

---

## 🚦 Connection Status States

### Connection Status Object
```typescript
connectionStatus: {
  websocket: boolean,   // Frontend ↔ Node Gateway WebSocket
  market_data: boolean, // Receiving market_data messages
  ibkr: boolean         // Python ↔ IBKR connection
}
```

### Status Flow
```
Initial:
  { websocket: false, market_data: false, ibkr: false }
  ↓
Connecting:
  { websocket: true, market_data: false, ibkr: false }
  ↓
Receiving first tick:
  { websocket: true, market_data: true, ibkr: false }
  ↓
Connection confirmed:
  { websocket: true, market_data: true, ibkr: true }
```

---

## 🧪 Testing Each Layer

### Test 1: Python → Node Gateway
```bash
# Watch Node Gateway logs for:
# "✅ Connected to Python IBKR Stream"
# "📊 Received market data from Python: EURUSD (50 messages)"
```

### Test 2: Node Gateway → Frontend
```bash
# Open browser DevTools → Network → WS
# Should see multiple "market_data" messages
# Each with symbol, bid, ask, candle data
```

### Test 3: Frontend Processing
```bash
# Browser console should show:
# "[useLiveFeed] ✅ WebSocket connection established"
# "[useLiveFeed] Received message #50: ..."
# "[TradingChart] EURUSD marketData: ..."
```

### Test 4: Chart Rendering
```bash
# Chart should show:
# - Current bid/ask/mid prices
# - "Waiting for candle data..." message initially
# - After 1-2 minutes: actual candlesticks
# - Green candles (close > open)
# - Red candles (close < open)
```

---

## 🔌 Environment Variables

### Node Gateway (.env or docker-compose)
```
PORT=8080
GRPC_HOST=localhost
GRPC_PORT=50051
```

### Frontend (vite.config.ts)
```
VITE_WS_URL=ws://localhost:8080/ws  (dev)
VITE_WS_URL=ws://your-domain:8080/ws (production)
```

### Python (ibkr_streaming/config.py)
```
NODE_GATEWAY_WS_URL=ws://localhost:8080/ws
```

---

## 💡 Pro Tips

1. **Monitor all three simultaneously**:
   - Python terminal: Watch for tick processing
   - Node terminal: Watch for broadcasts
   - Browser console: Watch for message received

2. **If chart is stuck on "Waiting for candle data..."**:
   - Candles take 1-2 minutes to form for 1m timeframe
   - Check if `marketData.candle` exists in browser console
   - Verify timestamp is Unix seconds (not milliseconds)

3. **Maximize data flow visibility**:
   - Add `console.log()` in each layer
   - Track message counts
   - Log transformation steps
   - Time each step

4. **Performance**: 
   - Frontend processes ~2.5 ticks/second
   - Candle cache limited to 500 per symbol
   - Browser should handle 5+ symbols simultaneously

---

## 📚 Files to Understand

| File | Purpose | Key Function |
|------|---------|--------------|
| `ibkr_streaming/run.py` | Main loop | Tick collection & WebSocket send |
| `ibkr_streaming/tick_stream.py` | IBKR connector | Live market data extraction |
| `ibkr_streaming/candle_engine.py` | Candle builder | OHLC aggregation by timeframe |
| `node_gateway/src/index.ts` | Server | WebSocket routing |
| `node_gateway/src/websockets/market.stream.ts` | Normalizer | Message transformation |
| `node_gateway/src/websockets/client.manager.ts` | Broadcaster | Client message delivery |
| `frontend/src/hooks/useLiveFeed.ts` | Data layer | State management & connection |
| `frontend/src/components/TradingChart.tsx` | Chart prep | Candle extraction & caching |
| `frontend/src/components/PriceChart.tsx` | Renderer | lightweight-charts wrapper |

---

## 🎯 Success Metrics

✅ **Data Flow Success**: See "Received message #X" in browser console every 0.4 seconds
✅ **Candle Formation**: After 1-2 minutes, chart shows at least 1 candlestick
✅ **Real-time Update**: Bid/Ask/Mid prices update without page refresh
✅ **Multi-symbol Support**: Switch symbols and see different charts
✅ **No Errors**: Zero errors in browser console, Python logs, Node logs
