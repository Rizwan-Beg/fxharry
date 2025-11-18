# 🚀 Quick Start - Get Data Rendering NOW

## Step 1: Verify All Services Start Correctly (2 minutes)

### Terminal 1: Python IBKR Streaming
```bash
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main
source .venv/bin/activate
python -m ibkr_streaming.run
```

✅ You should see:
```
✅ WebSocket connected to Node Gateway at ws://localhost:8080/ws
📊 Received market data from Python: EURUSD (50 messages)
Processed 100 ticks | Symbol: EURUSD | Bid: 1.0847 | Ask: 1.0849
```

### Terminal 2: Node Gateway
```bash
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/node_gateway
npm install  # Only first time
npm start
```

✅ You should see:
```
✅ Node Gateway listening on http://0.0.0.0:8080
✅ WebSocket server ready at ws://localhost:8080/ws
✅ Connected to Python IBKR Stream
✅ Frontend WebSocket connected (Total clients: 1)
```

### Terminal 3: Frontend
```bash
cd /Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/frontend
npm install  # Only first time
npm run dev
```

✅ You should see:
```
  ➜ Local:   http://localhost:5173/
  ➜ press h to show help
```

---

## Step 2: Open Frontend in Browser (5 seconds)

```
http://localhost:5173/
```

✅ You should see:
- Header: "AI Forex Trading Dashboard"
- Connection Status indicator (should turn green)
- Price charts (might show "Waiting for candle data...")

---

## Step 3: Verify WebSocket Connection (30 seconds)

### Open Browser DevTools (F12)
- Go to **Console** tab
- You should see logs like:

```
[useLiveFeed] Connecting to WebSocket: ws://localhost:8080/ws
✅ [useLiveFeed] WebSocket connection established
```

### Alternative: Network → WS Tab
- Should show connection to `ws://localhost:8080/ws`
- Status: **101 Switching Protocols**
- Messages flowing from server

✅ If you see errors here → **STOP & Debug Connection Section Below**

---

## Step 4: Monitor Data Flow (1 minute)

Keep browser console open and watch for:

```
[useLiveFeed] Received message #50: {
  type: 'market_data',
  symbol: 'EURUSD',
  hasCandle: true,
  bid: 1.0847,
  ask: 1.0849
}
```

✅ If these appear every ~2 seconds → **Data is flowing!**

---

## Step 5: Wait for Chart Rendering (1-2 minutes)

The chart will show stages:

### Stage 1: Waiting
```
[ Waiting for market data... ]
Current Price: 1.0847
```

### Stage 2: Initial Data
```
[ Waiting for candle data... ]
Current Price: 1.0847
Bid: 1.0847 | Ask: 1.0849 | Mid: 1.0848 | Spread: 0.0002
```

### Stage 3: Candles Forming ✅
```
[Actual candlestick chart appears here]
Green and red candles showing OHLC data
```

---

## ⚠️ **IF DATA ISN'T RENDERING**

### Check 1: Python Running?
```bash
# In another terminal
ps aux | grep "ibkr_streaming"
```
✅ Should show: `python -m ibkr_streaming.run`

### Check 2: Node Gateway Running?
```bash
ps aux | grep "node"
```
✅ Should show: Node process on port 8080

### Check 3: Frontend Running?
```bash
ps aux | grep "vite"
```
✅ Should show: Vite dev server on port 5173

### Check 4: Ports Available?
```bash
lsof -i :8080   # Should show Node Gateway
lsof -i :5173   # Should show Frontend
```

If port in use:
```bash
# Kill the process using the port
kill -9 <PID>
```

### Check 5: Browser Console for Errors
Open DevTools → Console
❌ Red errors = Problem!
✅ No red errors = Should work

### Check 6: Network Connection
Browser DevTools → Network → WS
- Should see `ws://localhost:8080/ws`
- Status: 101
- Messages flowing (click to see messages)

---

## 🔄 **IF SOMETHING BREAKS**

### Restart Everything (Clean)
```bash
# Kill all Python/Node/npm processes
killall -9 python node npm

# Wait 2 seconds
sleep 2

# Start in order:
# 1. Terminal 1: Python
# 2. Terminal 2: Node
# 3. Terminal 3: Frontend
# 4. Browser: Refresh page (F5)
```

### Clear Browser Cache
```bash
# Hard refresh
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# Or in DevTools:
Right-click refresh icon → "Empty cache and hard refresh"
```

### Check Logs for Errors
```bash
# Python terminal
# Look for: ❌ or error messages

# Node terminal  
# Look for: error, Error, ERROR

# Browser console
# Look for: Red messages or CORS errors
```

---

## ✅ **SUCCESS CHECKLIST**

- [ ] Python terminal shows "Processed X ticks"
- [ ] Node terminal shows "Received market data from Python"
- [ ] Node terminal shows "Frontend WebSocket connected"
- [ ] Browser console shows "WebSocket connection established"
- [ ] Browser console shows "Received message #50" (and increments)
- [ ] Chart shows bid/ask/mid prices updating
- [ ] After 1-2 minutes, chart shows candlesticks
- [ ] Connection Status indicator is green
- [ ] No red errors in browser console
- [ ] Can switch between EURUSD/GBPUSD/USDJPY symbols

---

## 🎯 **EXPECTED BEHAVIOR**

| Time | What Happens | Where to See It |
|------|--------------|-----------------|
| 0s | Services start | Terminal windows |
| 10s | Frontend loads | Browser page |
| 15s | WebSocket connects | Browser console log |
| 20s | First tick received | Browser console + prices update |
| 30s | Data flowing smoothly | Every 0.4s new message received |
| 2 min | First candle formed | Chart shows 1 candlestick |
| 5 min | Multiple candles | Chart shows 5+ candlesticks pattern |
| 10 min | Smooth real-time updates | Chart continuously updating |

---

## 📞 **QUICK FIXES FOR COMMON ISSUES**

### "No candles showing even after 5 minutes"
→ Check if candle data is in the messages: Open DevTools → Network → WS → Click a message → Look for `"candle": {...}`
→ If missing: Might need to wait for first 1m window to close

### "Chart shows 'Waiting for market data...'"
→ Messages not arriving
→ Check browser console for WebSocket errors
→ Verify Node Gateway is running: `curl http://localhost:8080/api/health`

### "Numbers keep changing but chart won't render"
→ Data flowing but chart library issue
→ Refresh browser page (F5)
→ Check browser console for chart errors
→ Try different symbol button

### "Everything was working then stopped"
→ One service crashed
→ Check all three terminals for errors
→ Restart the broken service
→ Refresh browser

### "Port 8080 already in use"
→ Run: `lsof -i :8080`
→ Kill the process: `kill -9 <PID>`
→ Restart Node Gateway

### "CORS errors in browser console"
→ Frontend can't reach Node Gateway
→ Verify Node is running: `curl http://localhost:8080/api/health`
→ Check firewall settings
→ Make sure using `ws://localhost:8080` not `ws://127.0.0.1`

---

## 🎓 **WHAT'S HAPPENING UNDER THE HOOD**

1. **Python** connects to Interactive Brokers API
2. **Python** gets real-time bid/ask prices
3. **Python** aggregates into 1m/5m/15m/1h/4h candles
4. **Python** sends WebSocket message to Node Gateway every ~0.4 seconds
5. **Node Gateway** receives message, normalizes it, broadcasts to all connected browsers
6. **React Frontend** receives message, updates state
7. **TradingChart component** converts to candle format
8. **PriceChart component** (lightweight-charts) renders candlestick
9. **Browser** displays real-time chart with updating prices

---

## 📊 **DATA JOURNEY VISUALIZATION**

```
IBKR API
   ↓ (bid/ask every 100ms)
Python TickStreamer
   ↓ (batched every 0.4s)
CandleEngine (builds 1m, 5m, etc.)
   ↓ (converts to JSON)
WebSocket: ws://localhost:8080
   ↓
Node Gateway (receives & broadcasts)
   ↓ (normalized to market_data)
Browser WebSocket
   ↓
React useLiveFeed Hook
   ↓ (updates state)
TradingChart Component
   ↓ (extracts candles)
PriceChart (lightweight-charts)
   ↓
🎯 Candlestick Chart on Screen
```

---

## 🚀 **NEXT STEPS**

Once data is rendering:

1. **Add more symbols**: Edit `ibkr_streaming/symbols.py`
2. **Change timeframes**: Edit `CandleEngine.TIMEFRAMES`
3. **Add indicators**: Add to TradingChart component
4. **Deploy**: Use docker-compose for production

---

## 📞 **STILL STUCK?**

Run this diagnostic script:

```bash
echo "=== DIAGNOSTIC REPORT ==="
echo "1. Python process:"
ps aux | grep ibkr_streaming || echo "NOT RUNNING"

echo "\n2. Node process:"
ps aux | grep node | grep -v grep || echo "NOT RUNNING"

echo "\n3. Port 8080:"
lsof -i :8080 || echo "FREE"

echo "\n4. Port 5173:"
lsof -i :5173 || echo "FREE"

echo "\n5. Node Gateway health:"
curl -s http://localhost:8080/api/health || echo "UNREACHABLE"

echo "\n6. Files modified today:"
find . -mtime -1 -type f | grep -E "(run.py|market.stream|useLiveFeed|TradingChart)" | head -5
```

Save output and check each item ✅
