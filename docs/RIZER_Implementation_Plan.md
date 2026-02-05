# RIZER Strategy Implementation Plan

## Overview

Implementing a production-grade, 9-stage modular trading strategy for EUR/USD on 5-minute timeframe. Each stage operates independently with strict type interfaces and deterministic outputs.

## Architecture Design

### Modular Structure

```
ai_core/strategy_engine/rizer/
├── __init__.py
├── config.py                    # Strategy configuration
├── stages/
│   ├── __init__.py
│   ├── stage_0_kill_switch.py   # Global hard gate
│   ├── stage_1_session.py       # Session filter
│   ├── stage_2_regime.py        # ADX-based regime
│   ├── stage_3_participation.py # VWAP filter
│   ├── stage_4_directional.py   # EMA structure
│   ├── stage_5_timing.py        # RSI regime
│   ├── stage_6_ml_edge.py       # ML scoring
│   ├── stage_7_decision.py      # Weighted aggregation
│   ├── stage_8_risk.py          # ATR-based risk
│   └── stage_9_monitor.py       # Trade monitoring
├── indicators/
│   ├── __init__.py
│   ├── adx.py                   # ADX calculation
│   ├── vwap.py                  # VWAP calculation
│   └── utils.py                 # Shared utilities
└── rizer_strategy.py            # Main orchestrator
```

### Data Flow

```
Market Data → Stage 0 (Kill Switch) → Stage 1 (Session) → 
Stages 2-6 (Scoring) → Stage 7 (Decision) → Stage 8 (Risk) → Signal
                                                                ↓
                                        Stage 9 (Monitor) → Exit Signal
```

## Detailed Component Breakdown

### Core Infrastructure

#### Indicators Module

##### ADX Indicator
- **Purpose**: Measure trend strength for regime classification
- **Inputs**: High, Low, Close prices; period=14
- **Output**: ADX value (0-100)
- **Implementation**: Wilder's smoothing method, no lookahead

##### VWAP Indicator
- **Purpose**: Institutional participation level
- **Inputs**: Price, Volume for session
- **Output**: VWAP value
- **Reset**: Per trading session

### Stage Implementations

#### Stage 0: Global Kill Switch
**Purpose**: Hard gate for data quality and external events

**Inputs**:
- `spread`: float
- `data_timestamp`: datetime
- `news_events`: List[NewsEvent]

**Logic**:
- Spread > 2 pips → kill
- Data staleness > 30s → kill  
- High-impact news ±30min → kill

**Output**: `{kill_switch: bool, reason: str}`

---

#### Stage 1: Session Filter
**Purpose**: London/New York session validation

**Integration**: Use existing `market_session.py`

**Output**: `{session_allowed: bool, current_session: str}`

---

#### Stage 2: Market Regime (ADX)
**Purpose**: Classify market condition by trend strength

**Input**: ADX(14)

**Scoring Logic**:
```python
if adx < 15:
    regime_score = 0.0      # Choppy/ranging
elif adx < 20:
    regime_score = 0.3      # Weak trend forming
elif adx < 30:
    regime_score = 0.6      # Moderate trend
else:
    regime_score = 0.9      # Strong trend
```

**Output**: `{regime_score: float, adx_value: float, regime_type: str}`

---

#### Stage 3: Participation (VWAP)
**Purpose**: Measure institutional participation via VWAP

**Inputs**:
- `vwap`: float
- `price`: float  
- `atr_14`: float

**Scoring Logic**:
```python
distance = (price - vwap) / atr_14

if abs(distance) > 1.0:
    # Extended from VWAP
    participation_score = -distance  # Fade extended moves
elif price > vwap and (price - vwap) > 0:
    # Reclaimed and holding VWAP
    participation_score = +0.7
elif abs(distance) < 0.2:
    # Choppy around VWAP
    participation_score = 0.0
else:
    participation_score = distance * 0.5
```

**Output**: `{participation_score: float, vwap_distance_atr: float}`

---

#### Stage 4: Directional Bias (EMA)
**Purpose**: Determine trend direction and strength

**Inputs**: EMA(20), EMA(50), EMA(100)

**Logic**:
```python
# LONG bias
if ema_20 > ema_50 > ema_100:
    directional_bias = "LONG"
    # Strength based on separation
    sep = ((ema_20 - ema_100) / ema_100) * 100
    trend_score = min(1.0, sep * 10)  # Scale to [0, 1]
    
# SHORT bias  
elif ema_20 < ema_50 < ema_100:
    directional_bias = "SHORT"
    sep = ((ema_100 - ema_20) / ema_100) * 100
    trend_score = -min(1.0, sep * 10)
    
# NEUTRAL
else:
    directional_bias = "NEUTRAL"
    trend_score = 0.0
```

**Output**: `{directional_bias: str, trend_score: float, ema_alignment: bool}`

---

#### Stage 5: Timing (RSI)
**Purpose**: Refine entry timing within trend

**Input**: RSI(14)

**Scoring Logic**:
```python
if rsi < 30:
    timing_score = +0.5      # Oversold in uptrend = buy timing
elif rsi < 40:
    timing_score = +0.3      # Pullback in uptrend
elif rsi > 70:
    timing_score = -0.5      # Overbought in downtrend = sell timing
elif rsi > 60:
    timing_score = -0.3      # Pullback in downtrend
else:
    timing_score = 0.0       # Neutral
```

**Output**: `{timing_score: float, rsi_value: float, rsi_regime: str}`

---

#### Stage 6: ML Edge
**Purpose**: Statistical edge via machine learning

**Feature Vector**:
- `regime_score`
- `participation_score`
- `trend_score`
- `timing_score`
- `price_momentum`
- `volatility_percentile`

**Model**: Lightweight gradient boosting or logistic regression

**Output**: `{ml_edge_score: float, confidence: float, feature_importance: dict}`

**Phase 1 Implementation**: Placeholder returning 0.0 (no edge)

---

#### Stage 7: Decision Engine
**Purpose**: Aggregate all signals with weighted scoring

**Weights**:
- `regime_score`: 0.15
- `participation_score`: 0.25
- `trend_score`: 0.20
- `timing_score`: 0.10
- `ml_edge_score`: 0.30

**Logic**:
```python
final_score = (
    regime_score * 0.15 +
    participation_score * 0.25 +
    trend_score * 0.20 +
    timing_score * 0.10 +
    ml_edge_score * 0.30
)

if final_score >= 0.35:
    signal = "LONG"
elif final_score <= -0.35:
    signal = "SHORT"
else:
    signal = None  # No trade
```

**Output**: `{signal: str, final_score: float, breakdown: dict}`

---

#### Stage 8: Risk Management
**Purpose**: ATR-based position sizing and SL/TP

**Inputs**:
- `atr_14`: float
- `account_equity`: float
- `signal`: str

**Logic**:
```python
stop_loss = 1.2 * atr_14
take_profit = 2.0 * stop_loss

# Risk 1% of equity per trade
risk_per_trade = account_equity * 0.01
position_size = risk_per_trade / stop_loss

# Volatility scaling
if atr_14 > recent_avg_atr * 1.5:
    position_size *= 0.7  # Reduce size in high volatility
```

**Output**: `{stop_loss: float, take_profit: float, position_size: float}`

---

#### Stage 9: Trade Monitoring
**Purpose**: Continuous re-evaluation for early exits

**Re-evaluate Every Candle**:
- VWAP reclaimed/lost
- EMA structure breaks
- Momentum decay (RSI reversal)

**Exit Conditions**:
```python
# Long position exits
if in_long:
    if price < vwap and previously_above:
        exit_reason = "VWAP_VIOLATION"
    elif ema_20 < ema_50:
        exit_reason = "STRUCTURE_BREAK"
    elif rsi > 70:
        exit_reason = "MOMENTUM_EXHAUSTION"
```

**Output**: `{should_exit: bool, exit_reason: str}`

---

### Main RIZER Strategy Class

**Interface**:
```python
class RizerStrategy:
    def generate_signal(self, symbol, price, features):
        # Orchestrate all stages
        # Return signal dict or None
```

## Implementation Phases

### Phase 1: Core Infrastructure ✓
- ✓ Session filter (already exists)
- [x] Create RIZER directory structure
- [x] Implement indicators (ADX, VWAP)
- [x] Create config module

### Phase 2: Stage Implementation
- [x] Stages 0-5 (filters and scoring)
- [x] Stage 6 (ML placeholder)
- [x] Stages 7-9 (decision, risk, monitor)

### Phase 3: Integration
- [x] Main RIZER strategy class
- [x] Feature engine integration
- [x] Signal generation pipeline

### Phase 4: Testing & Validation
- [x] Unit tests for each stage
- [x] Integration tests
- [x] Backtest validation

## Verification Plan

### Unit Tests
- Test each stage in isolation with mock data
- Verify score ranges ([0,1], [-1,1], etc.)
- Test edge cases (missing data, extremes)

### Integration Tests
- End-to-end signal generation
- Verify no lookahead bias
- Confirm deterministic outputs

### Backtest
- Historical EUR/USD 5-min data
- Validate signal quality
- Measure risk-adjusted returns

## Next Steps

1. Create directory structure
2. Implement indicators (ADX, VWAP)
3. Build stages 0-5
4. Build stages 6-9
5. Create main orchestrator
6. Write tests
7. Run backtests
