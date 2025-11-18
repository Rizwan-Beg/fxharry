# Frontend Data Rendering - Debug & Verification Guide

## 🔍 **What I Fixed**

### **1. Python WebSocket Message Format** ✅
- **File**: `ibkr_streaming/run.py`
- **Issue**: Messages were incomplete
- **Fix**: Enhanced message structure to include:
  - `type: "tick"` - explicitly set
  - `candle`: Latest 1-minute candle
  - `candles`: All timeframes (1m, 5m, 15m, 1h, 4h)
  - Proper float conversion for all numeric values

### **2. Node Gateway Data Normalization** ✅
- **File**: `node_gateway/src/websockets/market.stream.ts`
- **Issue**: Candle extraction logic was complex and fragile
- **Fix**: Simplified normalization to:
  - Handle both `candles` object and single `candle` format
  - Properly extract 1m timeframe
  - Include all timeframes in normalized output
  - Fallback gracefully to tick data if no candles

### **3. Frontend WebSocket Hook** ✅
- **File**: `frontend/src/hooks/useLiveFeed.ts`
- **Issue**: Silent failures, no visibility
- **Fix**: Added comprehensive logging:
  - Connection establishment logging
  - Message count tracking (logs every 50th message)
  - Symbol-specific data updates
  - Connection status changes

### **4. Trading Chart Component** ✅
- **File**: `frontend/src/components/TradingChart.tsx`
- **Issue**: Timestamp handling and candle validation
- **Fix**: 
  - Support both milliseconds and seconds timestamps
  - Better candle validation
  - Improved fallback logic for incomplete data

---

## 🚀 **Quick Start Verification**

### **Step 1: Start Everything**

```bash
# Terminal 1 - Python IBKR Streaming
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main
source .venv/bin/activate
python -m ibkr_streaming.run

# Terminal 2 - Node Gateway
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/node_gateway
npm install
npm start

# Terminal 3 - Frontend
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/frontend
npm install
npm run dev
```

### **Step 2: Check the Console Logs**

Open your browser DevTools (F12) and look for these logs:

```
✅ [useLiveFeed] WebSocket connection established
📊 [useLiveFeed] Received message #50: 
   { type: 'market_data', symbol: 'EURUSD', hasCandle: true, bid: 1.0847, ask: 1.0849 }
```

### **Step 3: Verify Data Flow**

#### **Python IBKR Side**
You should see in the Python logs:
```
📊 Received market data from Python: EURUSD (50 messages)
Processed 100 ticks | Symbol: EURUSD | Bid: 1.0847 | Ask: 1.0849 | Mid: 1.0848
```

#### **Node Gateway Side**
You should see:
```
✅ Connected to Python IBKR Stream
✅ Frontend WebSocket connected (Total clients: 1)
📊 Received market data from Python: EURUSD (50 messages)
```

#### **Frontend Console**
You should see:
```
[useLiveFeed] Connecting to WebSocket: ws://localhost:8080/ws
✅ [useLiveFeed] WebSocket connection established
[useLiveFeed] Received message #50: {type: 'market_data', symbol: 'EURUSD', ...}
[TradingChart] EURUSD marketData: {hasCandle: true, candlesCount: 15, ...}
```

---

## 🔧 **Troubleshooting**

### **Problem: "No clients connected - data not broadcast"**
**Solution**: 
- Frontend WebSocket connection failed
- Check browser DevTools → Console for connection errors
- Verify Node Gateway is running on port 8080
- Check firewall/network settings

### **Problem: "Received message #X but chart stays empty"**
**Solution**:
- Data is arriving but not rendering
- Check if `hasCandle: true` in logs
- Check timestamp format (should be Unix seconds, not milliseconds)
- Browser console should show chart updates

### **Problem: "WebSocket connection closed immediately"**
**Solution**:
- Node Gateway not running
- Port 8080 already in use: `lsof -i :8080` then `kill -9 <PID>`
- Python still sending messages but Node Gateway crashed

### **Problem: Empty chart despite data flow**
**Solution**:
- Candles are being created but not displayed
- Lightweight-charts requires valid OHLC data
- Check candle validation: `open > 0, high >= low`
- Wait 1-2 minutes for first candle to form (depends on timeframe)

---

## 📊 **Expected Behavior Timeline**

### **T+0 seconds**
- Frontend connects to WebSocket
- Python connects and sends first tick
- Node Gateway routes data to frontend

### **T+5-10 seconds**
- First `market_data` messages appear in browser console
- Current bid/ask/mid prices displayed

### **T+1-2 minutes** (for 1m candles)
- First complete candle formed
- Chart renders with candle visible

### **T+3-5 minutes**
- Multiple candles visible on chart
- Candlestick pattern forming

---

## 🎯 **What You Should See**

### **Chart Rendering:**
✅ Green/Red candlesticks based on open/close
✅ Wicks showing high/low prices
✅ Multiple candles forming over time
✅ Real-time updates as new data arrives

### **Price Display:**
✅ Bid/Ask/Mid prices updating
✅ Spread calculation showing (Ask - Bid)
✅ Connection status indicator green

### **Console Logs:**
✅ Regular "[useLiveFeed] Received message #X" entries
✅ No error messages
✅ Connection status showing `ibkr: true, websocket: true, market_data: true`

---

## 🐛 **Advanced Debugging**

### **Enable Verbose Logging in Python**
Edit `ibkr_streaming/run.py` - change logging level to DEBUG:
```python
logger.setLevel(logging.DEBUG)  # More detailed logs
```

### **Monitor WebSocket Messages**
In browser DevTools → Network → WS → Messages tab:
- Should see continuous messages from server
- Each message should have `type: "market_data"`

### **Check Node Gateway Health**
```bash
curl http://localhost:8080/api/health
# Should return: {"status":"ok","grpc":"localhost:50051","timestamp":"..."}
```

### **Test Frontend Reconnection**
- Close Python streaming
- Watch frontend automatically reconnect after 3 seconds
- When Python comes back online, data should resume flowing

---

## ✅ **Success Checklist**

- [ ] Python IBKR streaming is running and sending ticks
- [ ] Node Gateway is running and receiving Python data
- [ ] Frontend WebSocket connects without errors
- [ ] Browser console shows "[useLiveFeed] WebSocket connection established"
- [ ] Browser console shows regular message log entries
- [ ] Chart area shows "Waiting for candle data..." (not error state)
- [ ] Bid/Ask/Mid prices are updating
- [ ] After 1-2 minutes, chart shows candlestick(s)
- [ ] Connection status indicator shows green

---

## 📞 **If Issues Persist**

1. **Check all services are running**:
   ```bash
   # Python
   ps aux | grep "python.*ibkr_streaming"
   
   # Node
   ps aux | grep "npm.*gateway"
   ps aux | grep "node"
   
   # Check ports
   lsof -i :8080  # Node Gateway
   lsof -i :3000  # Frontend dev server
   ```

2. **Verify no errors in logs**:
   - Look for Python exceptions in terminal
   - Look for Node errors in terminal
   - Look for WebSocket errors in browser console

3. **Check network connectivity**:
   - `curl http://localhost:8080/api/health`
   - Check browser DevTools → Network tab
   - Verify WebSocket shows "101 Switching Protocols"

4. **Reset everything**:
   ```bash
   # Kill all processes
   killall python node npm
   
   # Start fresh in order:
   # 1. Python
   # 2. Node Gateway
   # 3. Frontend
   ```

---

## 📝 **Files Modified**

1. `ibkr_streaming/run.py` - Enhanced message format
2. `node_gateway/src/websockets/market.stream.ts` - Simplified normalization
3. `frontend/src/hooks/useLiveFeed.ts` - Added comprehensive logging
4. `frontend/src/components/TradingChart.tsx` - Better data handling

All changes are backward compatible and focus on robustness over the existing logic.
