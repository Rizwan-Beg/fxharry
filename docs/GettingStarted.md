# Getting Started - FXHarry AI Trading System

This guide explains how to run the **complete end-to-end trading application**, including IBKR data streaming, Apex strategy execution, and automated order placement.

## 📋 Prerequisites

### Software Requirements
- **Node.js** v18+ and npm
- **Python** 3.10+ with pip
- **IBKR TWS or IB Gateway** running locally

### IBKR Configuration
- **Host**: `127.0.0.1`
- **Port**: 
  - `7497` for Paper Trading (recommended for testing)
  - `7496` for Live Trading
- **API Settings** (in TWS):
  - `File → Global Configuration → API → Settings`
  - ✅ Enable "Enable ActiveX and Socket Clients"
  - ✅ Socket port: 7497 (Paper) or 7496 (Live)
  - ✅ Read-only API: **Unchecked**
  - ✅ Create API message log file: **Checked** (for debugging)

### Python Dependencies
Required packages (should already be installed):
```bash
pip install ib_async websockets sqlalchemy psycopg2-binary
```

---

## 🚀 Quick Start

### Option 1: Full Application (Recommended)

Run all components together for the complete trading experience:

#### Terminal 1: Start Node Gateway
```bash
cd node_gateway
npm start
```

**Expected Output**:
```
✅ Node Gateway listening on http://0.0.0.0:8080
✅ WebSocket server ready at ws://localhost:8080/ws
```

#### Terminal 2: Start Frontend (Optional)
```bash
cd frontend
npm run dev
```

**Open**: `http://localhost:5173/`

#### Terminal 3: Start IBKR Streaming + Strategy + Execution
```bash
python3 -m ibkr_streaming.run
```

**Expected Output**:
```
✅ Connected to IBKR TWS/Gateway
✅ Broker Status: connected
✅ Execution Engine: ENABLED
✅ Execution Mode: PAPER_TRADING
✅ Subscribed symbols: ['EUR/USD', 'GBP/USD', 'XAU/USD', ...]
```

**What Happens**:
1. Connects to IBKR and streams real-time tick data
2. Builds M5 and M15 candles from ticks
3. Apex strategy monitors for trading signals
4. When conditions are met → generates signal → executes trade
5. All data is broadcast to frontend via WebSocket

---

### Option 2: Backend Only (No Frontend)

If you only want to run the trading engine without the UI:

```bash
python3 -m ibkr_streaming.run
```

This will:
- ✅ Stream data from IBKR
- ✅ Run Apex strategy
- ✅ Execute trades (PAPER mode by default)
- ❌ No visual dashboard

---

## 🎯 Testing the System

### Test 1: Simple Order Placement

Verify you can place orders in IBKR TWS:

```bash
python3 test_order_ib_async.py
```

**What it does**: Places a 1,000 EUR/USD BUY order and shows confirmation

**Expected**: Order appears in TWS Order Management tab

### Test 2: Integration Test

Test the complete flow with a simulated signal:

```bash
python3 test_integration.py
```

**What it does**: 
- Connects broker → execution engine
- Simulates Apex strategy signal
- Processes through risk manager
- Places order (simulated in PAPER mode)

---

## ⚙️ Configuration

### Execution Mode

**File**: `ai_core/execution/execution_config.py`

```python
# Safe default - orders are simulated
EXECUTION_MODE = ExecutionMode.PAPER_TRADING

# For live trading - real orders with real capital
# EXECUTION_MODE = ExecutionMode.LIVE_TRADING
```

**PAPER_TRADING Mode** (Default):
- ✅ Broker is connected
- ✅ Signals are processed
- ✅ Risk checks performed
- ⚠️ Orders are **simulated** (not sent to broker)
- ✅ Safe for testing

**LIVE_TRADING Mode**:
- ✅ All of the above
- ⚠️ **Real orders sent to IBKR**
- ⚠️ **Real capital at risk**

> **⚠️ WARNING**: Only switch to LIVE_TRADING after thorough testing in PAPER mode!

### IBKR Connection

**File**: `ibkr_streaming/config.py` (if it exists) or configure via code:
- `IBKR_HOST`: Usually `127.0.0.1`
- `IBKR_PORT`: `7497` (paper) or `7496` (live)
- `IBKR_CLIENT_ID`: Unique ID for this connection (default: `998`)

### Frontend WebSocket

**File**: `frontend/src/services/ws.ts`
- Default: `ws://localhost:8080/ws`
- Override via `VITE_WS_URL` environment variable

---

## 📊 Data Flow

```
IBKR TWS
   ↓ (Real-time Ticks)
TickStreamer
   ↓ (Tick Data)
CandleEngine
   ↓ (M5/M15 Candles)
Apex Strategy
   ↓ (Trading Signals)
SignalRouter
   ↓ (Signals)
ExecutionEngine → RiskManager
   ↓ (Approved Orders)
IBKRAsyncService
   ↓ (Orders)
IBKR TWS (Order Execution)
   ↓ (Market Data & Fills)
Frontend (WebSocket) → Dashboard Display
```

---

## 🔍 Monitoring

### Check Logs

Application logs appear in the terminal:
```bash
python3 -m ibkr_streaming.run
```

**Key Messages**:
```
✅ Connected to IBKR TWS/Gateway
✅ Execution Engine: ENABLED
✅ Execution Mode: PAPER_TRADING
✅ Subscribed symbols: [...]
```

**Signal Generation**:
```
Signals generated for EUR/USD: [{'strategy_id': 'apex', 'action': 'LONG', ...}]
```

**Order Execution**:
```
[PAPER TRADING] Simulating order: BUY 10000 EUR/USD
Position opened: BUY 10000 EUR/USD @ 1.1234
```

### Check IBKR TWS

**Order Management Tab**:
- Orders appear here when placed (LIVE mode only)
- Status: PendingSubmit → Submitted → Filled

**Portfolio Tab**:
- Shows open positions
- P&L updates in real-time

**Trade Log**:
- Execution details
- Fill prices, commissions

### Check Database

```bash
sqlite3 trading.db
```

```sql
-- View recent trades
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;

-- View signals
SELECT * FROM ai_signals ORDER BY timestamp DESC LIMIT 10;

-- View order events
SELECT * FROM order_events ORDER BY timestamp DESC LIMIT 10;
```

---

## ✅ Verify Connectivity

Quick diagnostic test:

```bash
python3 test_connections.py
```

**Expected**:
- HTTP Health: PASS
- WebSocket Connection: PASS

---

## 🐛 Troubleshooting

### Connection Refused Error

**Error**: `ConnectionRefusedError: [Errno 61] Connect call failed`

**Solution**:
1. ✅ Open IBKR TWS or IB Gateway
2. ✅ Check API settings are enabled (see Prerequisites)
3. ✅ Verify correct port (7497 for paper, 7496 for live)
4. ✅ Restart TWS if needed

### Port Already in Use

**Error**: `EADDRINUSE: 8080`

**Solution**:
- Stop other Node Gateway instances
- Or change port: `PORT=8081 npm start`

### IBKR Client ID Conflict

**Error**: `clientId already in use`

**Solution**:
- Change `client_id` in the broker initialization
- Different ID for each connection (e.g., 997, 998, 999)

### No Signals Generated

**Possible Causes**:
- Market conditions don't match Apex strategy criteria
- Insufficient candle history (wait 15+ minutes for M15 candles)
- Strategy requires specific M5/M15 SMA patterns

**Solution**:
- Use `test_integration.py` to inject a test signal
- Check logs for strategy evaluation messages
- Monitor M5/M15 candle formation

### Orders Not Appearing in TWS

**Possible Causes**:
- Running in PAPER_TRADING mode (orders are simulated)
- TWS API not enabled
- Connection issue

**Solution**:
1. Check execution mode in logs
2. Run `test_order_ib_async.py` to verify broker connectivity
3. Check TWS API logs for errors

---

## 📁 Project Structure

### Key Files

**Application Core**:
- `ibkr_streaming/run.py` - Main application entry point
- `ibkr_streaming/tick_stream.py` - IBKR data streaming
- `ibkr_streaming/candle_engine.py` - Candle formation

**Trading Strategy**:
- `ai_core/strategy_engine/strategies/apex_strategy.py` - Apex strategy logic
- `ai_core/strategy_engine/signal_router.py` - Signal routing

**Execution Engine**:
- `ai_core/execution/execution_engine.py` - Order execution logic
- `ai_core/execution/execution_config.py` - Execution configuration
- `ai_core/risk_manager/risk_manager.py` - Risk management

**Broker Integration**:
- `ai_core/strategy_engine/broker/ibkr_async_service.py` - IBKR broker adapter
- `ai_core/strategy_engine/broker/base_broker.py` - Broker interface

**Frontend**:
- `node_gateway/` - WebSocket gateway for frontend
- `frontend/` - React dashboard

**Tests**:
- `test_order_ib_async.py` - Simple order placement test
- `test_integration.py` - Full integration test
- `test_connections.py` - Connection diagnostic

---

## 🎓 Understanding the System

### Apex Strategy

Multi-timeframe trend-following strategy:
- **M15 Timeframe**: Defines directional bias using SMA(50)
- **M5 Timeframe**: Entry signals using SMA(10/30) crossover + RSI(14)
- **Sessions**: Trades during London/NY sessions (high liquidity)

**Entry Conditions** (LONG):
1. M15 SMA(50) shows uptrend
2. M5 SMA(10) crosses above SMA(30)
3. RSI(14) not overbought
4. Active trading session

**Exit Conditions**:
1. Opposite SMA crossover
2. M15 bias reversal
3. Stop-loss or take-profit hit

### Risk Management

**Circuit Breaker**:
- Stops trading after -1% daily loss
- Or after 3 consecutive losses

**Position Limits**:
- Max 5 concurrent positions
- Max 5 orders per minute

**Risk Assessment**:
- Each signal evaluated for risk
- Position sizing based on account balance
- Automatic rejection of high-risk trades

---

## 🚦 Next Steps

### For Testing
1. ✅ Run in PAPER_TRADING mode for 1-2 days
2. ✅ Monitor all signals and simulated trades
3. ✅ Verify risk management and circuit breaker
4. ✅ Check strategy performance

### For Production
1. ⏳ Backtest strategy on historical data
2. ⏳ Optimize parameters (SMA periods, RSI levels)
3. ⏳ Set appropriate risk limits
4. ⏳ Switch to LIVE_TRADING mode
5. ⏳ Start with micro positions (500-1000 units)
6. ⏳ Monitor first 10-20 trades closely
7. ⏳ Gradually increase position sizes

---

## 📚 Additional Documentation

- [Execution Engine Quick Start](EXECUTION_ENGINE_QUICKSTART.md) - Detailed execution engine guide
- [Walkthrough](../brain/walkthrough.md) - Recent integration walkthrough
- [Implementation Plan](../brain/implementation_plan.md) - Technical architecture

---

## ⚡ Quick Reference

### Start Everything
```bash
# Terminal 1
cd node_gateway && npm start

# Terminal 2  
cd frontend && npm run dev

# Terminal 3
python3 -m ibkr_streaming.run
```

### Test Order Placement
```bash
python3 test_order_ib_async.py
```

### Test Full Integration
```bash
python3 test_integration.py
```

### Stop Application
- Press `Ctrl+C` in each terminal
- Application will gracefully shutdown

---

## 💡 Tips

- **First Time Setup**: Start with PAPER_TRADING mode
- **Market Hours**: Forex markets trade 24/5, but liquidity is best during London/NY sessions
- **Signal Frequency**: Apex strategy may generate 1-3 signals per day depending on market conditions
- **Monitor Positions**: Always check TWS Portfolio tab to see current positions
- **Logs**: Keep terminal logs visible to monitor system health

---

## ✨ Success Indicators

Your system is working correctly when you see:

1. ✅ IBKR broker connected in logs
2. ✅ Tick data streaming every ~2.5 ticks/second
3. ✅ M5/M15 candles building properly
4. ✅ Strategy evaluating conditions
5. ✅ Signals generated when conditions met
6. ✅ Orders executed (simulated in PAPER mode)
7. ✅ Positions visible in TWS (LIVE mode)

**You're ready to trade!** 🚀