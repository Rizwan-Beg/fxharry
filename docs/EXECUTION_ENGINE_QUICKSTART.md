# Trade Execution Engine - Quick Start Guide

## Overview

The Trade Execution Engine is now integrated into your FXHarry trading system. It automatically executes trades based on signals from your Apex strategy.

## 🎯 Key Features

✅ **Paper Trading Mode** (default) - Test without risking real capital
✅ **Risk Management** - Automatic position sizing and risk checks
✅ **Circuit Breaker** - Auto-stops trading on excessive losses
✅ **Position Tracking** - Real-time P&L monitoring
✅ **Order Management** - Full order lifecycle tracking
✅ **Kill Switch** - Emergency stop for all trading

## 🚀 Getting Started

### 1. Current Configuration

The system is currently in **PAPER_TRADING** mode. This means:
- Signals are processed ✅
- Risk checks are performed ✅
- Trades are simulated ✅
- No real orders sent to broker ✅
- All data saved to database ✅

### 2. Running the System

```bash
# Terminal 1: Start Node Gateway
cd node_gateway && npm start

# Terminal 2: Start Frontend
cd frontend && npm run dev

# Terminal 3: Start IBKR Streaming (with execution engine)
python -m ibkr_streaming.run
```

### 3. Monitoring Execution

Watch the logs for execution engine activity:
```
[INFO] ExecutionEngine initialized
[INFO] Execution mode: PAPER_TRADING
[INFO] Processing signal: {'symbol': 'EUR/USD', 'action': 'LONG', ...}
[INFO] Risk assessment for EUR/USD: {...}
[INFO] [PAPER TRADING] Simulating order: ...
[INFO] Position opened: BUY 10000 EUR/USD @ 1.1000
```

## ⚙️ Configuration

Edit [`ai_core/execution/execution_config.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ai_core/execution/execution_config.py) to customize:

### Execution Mode
```python
EXECUTION_MODE = ExecutionMode.PAPER_TRADING  # Safe default
# EXECUTION_MODE = ExecutionMode.LIVE_TRADING  # For real trading
```

### Circuit Breaker
```python
CIRCUIT_BREAKER_LOSS_THRESHOLD = -0.01  # Stop after -1% daily loss
CIRCUIT_BREAKER_CONSECUTIVE_LOSSES = 3   # Stop after 3 losses in a row
```

### Risk Limits
```python
MAX_CONCURRENT_POSITIONS = 5      # Max open positions
MAX_ORDERS_PER_MINUTE = 5         # Rate limiting
MANUAL_APPROVAL_RISK_THRESHOLD = 0.7  # High-risk orders need approval
```

## 📊 Database Schema

New tables track execution:

**Trade Model** (enhanced):
- `broker_order_id` - Broker's order ID
- `order_status` - Order state
- `execution_mode` - PAPER or LIVE
- `risk_assessment` - Full risk check results

**AISignal Model** (enhanced):
- `execution_trade_id` - Link to executed trade
- `rejection_reason` - Why signal was rejected

## 🧪 Testing

Run the unit tests:
```bash
# Run all execution engine tests
python -m pytest ai_core/execution/tests/ -v

# Run specific test
python -m pytest ai_core/execution/tests/test_execution_engine.py::TestExecutionEngine::test_paper_trading_entry_signal -v
```

## 🔄 Switching to Live Trading

> [!WARNING]
> **Only switch to live trading after thorough testing in paper mode!**

1. **Verify paper trading works**:
   - Run for at least 1-2 days
   - Check all signals are processed correctly
   - Verify risk checks work
   - Test circuit breaker

2. **Initialize IBKR broker** in [`ibkr_streaming/run.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ibkr_streaming/run.py):
   ```python
   from ai_core.strategy_engine.broker.ibkr_service import IBKRService
   
   ibkr_service = IBKRService(host="127.0.0.1", port=7497, client_id=2)
   await ibkr_service.connect()
   
   execution_engine = ExecutionEngine(
       broker_service=ibkr_service,  # Now with real broker
       risk_manager=risk_manager
   )
   ```

3. **Change execution mode** in [`execution_config.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ai_core/execution/execution_config.py):
   ```python
   EXECUTION_MODE = ExecutionMode.LIVE_TRADING
   ```

4. **Start with small positions**:
   - Test with micro lots first
   - Monitor first 5-10 trades closely
   - Gradually increase position sizes

## 🚨 Emergency Controls

### Circuit Breaker Status
Check circuit breaker in logs or database:
```python
status = execution_engine.get_status()
print(status['circuit_breaker'])
```

### Manual Emergency Stop
If needed, trigger kill switch:
```python
execution_engine.emergency_stop()
```

Or set in config:
```python
ENABLE_KILL_SWITCH = True
```

### Reset Circuit Breaker
After fixing issues:
```python
execution_engine.circuit_breaker.reset(force=True)
execution_engine.enabled = True
```

## 📈 Monitoring & Metrics

### Position Tracker
```python
# Get all open positions
positions = execution_engine.position_tracker.get_stats()

# Check specific position
position = execution_engine.position_tracker.get_position('EUR/USD')
```

### Order Manager
```python
# Get order statistics
order_stats = execution_engine.order_manager.get_stats()

# Get specific order
order = execution_engine.order_manager.get_order(order_id)
```

### Execution Status
```python
status = execution_engine.get_status()
# Returns: {
#   'enabled': True/False,
#   'execution_mode': 'PAPER_TRADING',
#   'circuit_breaker': {...},
#   'orders': {...},
#   'positions': {...}
# }
```

## 📝 Signal Format

The execution engine expects signals in this format:

```python
signal = {
    'strategy_id': 'apex',           # Strategy identifier
    'symbol': 'EUR/USD',              # Trading symbol
    'action': 'LONG',                 # LONG, SHORT, or EXIT
    'price': 1.1000,                  # Entry price
    'stop_loss': 1.0900,              # Optional: SL price
    'take_profit': 1.1300,            # Optional: TP price
    'reason': 'M5 SMA crossover',     # Signal reason
    'timestamp': '2026-02-10T14:30:00'  # ISO format
}
```

## 🐛 Troubleshooting

**"Execution engine is disabled"**
- Check `execution_engine.enabled = True`
- Check circuit breaker status

**"Circuit breaker is tripped"**
- Review trip reason in logs
- Reset if appropriate
- Investigate underlying issue

**"Trade rejected by risk manager"**
- Check risk assessment in logs
- Verify position sizes
- Check daily loss limits

**Orders not executing**
- Verify execution mode
- Check broker connection (live mode)
- Review logs for errors

## 📚 Next Steps

1. ✅ **Paper Trading** - Run for 1-2 days
2. ✅ **Monitor Performance** - Check P&L, fill rates
3. ✅ **Fine-tune Parameters** - Adjust risk limits if needed
4. ⏳ **Live Trading** - Only after successful paper testing
5. ⏳ **Add Monitoring Dashboard** - UI for execution metrics

## 📞 Support

Check logs in:
- Console output
- `backend.log`
- Database `trades` and `order_events` tables

For issues, review:
- [`execution_engine.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ai_core/execution/execution_engine.py) - Main logic
- [`execution_config.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ai_core/execution/execution_config.py) - Configuration
- [`circuit_breaker.py`](file:///Users/rizwan/Devlopment/ai_quant_firm/fxharry-main/ai_core/execution/circuit_breaker.py) - Safety mechanism
