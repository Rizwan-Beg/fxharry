# Software Design Document (SDD)
## FXHarry - QuantX AI-Powered Trading System

**Document Version**: 1.0  
**Date**: January 2, 2026  
**Project**: FXHarry (QuantX)  
**Document Owner**: Rizwan Beg

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Component Design](#3-component-design)
4. [Data Design](#4-data-design)
5. [Interface Design](#5-interface-design)
6. [Deployment Architecture](#6-deployment-architecture)

---

## 1. Introduction

### 1.1 Purpose

This Software Design Document (SDD) describes the architectural design, component specifications, and technical implementation details of the FXHarry (QuantX) AI-Powered Trading System.

### 1.2 Scope

This document covers:
- High-level system architecture
- Component-level design specifications
- Data models and flows
- Interface specifications
- Deployment architecture
- Technology stack decisions

### 1.3 Design Goals

1. **Modularity**: Each component should be independently deployable and testable
2. **Scalability**: Support horizontal scaling for production deployment
3. **Real-Time Performance**: Sub-100ms latency for signal propagation
4. **Maintainability**: Clean architecture, well-documented, solo-maintainable
5. **Extensibility**: Plugin architecture for strategies and API integrations
6. **Reliability**: 99.9% uptime, automatic recovery from failures

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
graph TB
    subgraph External["External Systems"]
        IBKR[IBKR TWS/Gateway]
        APIs[Future APIs<br/>TradingView, Polygon, etc.]
    end
    
    subgraph Backend["Backend Layer"]
        IBKRStream[IBKR Streaming Service<br/>Python]
        AICore[AI Core<br/>Strategy Engine<br/>Python]
        NodeGW[Node Gateway<br/>TypeScript]
    end
    
    subgraph Frontend["Frontend Layer"]
        Dashboard[React Dashboard<br/>TypeScript]
    end
    
    subgraph Infrastructure["Infrastructure (Planned)"]
        DB[(PostgreSQL<br/>TimescaleDB)]
        MQ[Redis/Kafka<br/>Message Queue]
        Monitor[Prometheus<br/>Grafana]
    end
    
    IBKR -->|Market Data| IBKRStream
    APIs -.->|Future| NodeGW
    IBKRStream -->|Ticks + Candles| AICore
    AICore -->|Signals| IBKRStream
    IBKRStream -->|WebSocket| NodeGW
    NodeGW -->|WebSocket| Dashboard
    NodeGW -.->|Future| DB
    NodeGW -.->|Future| MQ
    AICore -.->|Future| DB
    NodeGW -.->|Metrics| Monitor
```

### 2.2 Architecture Pattern

**Pattern**: Layered + Event-Driven Architecture

**Layers**:
1. **Presentation Layer**: React frontend
2. **API Gateway Layer**: Node.js gateway for I/O orchestration
3. **Business Logic Layer**: Python AI Core for strategy execution
4. **Data Layer**: IBKR streaming service
5. **Infrastructure Layer**: Database, message queue, monitoring (planned)

**Communication**:
- **Real-time**: WebSocket for streaming data
- **Request/Response**: REST API (planned)
- **High-performance**: gRPC (optional, future)

### 2.3 Technology Stack Summary

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Modern, performant UI with type safety |
| **Styling** | TailwindCSS | Rapid development, consistent design |
| **Charts** | lightweight-charts | High-performance candlestick charts |
| **Gateway** | Node.js + Express + TypeScript | Excellent I/O performance, event-driven |
| **Real-time** | WebSocket (ws) | Low-latency bidirectional communication |
| **AI Engine** | Python 3.10+ | Industry standard for ML/quant |
| **Numerical** | NumPy, Pandas | Fast numerical computation |
| **ML/DL** | PyTorch | Flexible deep learning framework |
| **Broker** | Interactive Brokers (`ib_async`) | Professional-grade async broker API with bracket order support |
| **GenAI** | `llama-3.1-8b` | Real-time news sentiment and trade veto logic |
| **Database** | PostgreSQL + TimescaleDB (planned) | Reliable, time-series optimized |
| **Message Queue** | Redis/Kafka (planned) | Message reliability, pub/sub |
| **Monitoring** | Prometheus + Grafana (planned) | Metrics collection and visualization |
| **Containers** | Docker, Docker Compose | Consistent deployment |
| **Orchestration** | Kubernetes (planned) | Production-grade orchestration |

---

## 3. Component Design

### 3.1 Frontend (React Dashboard)

**Location**: `frontend/`

#### 3.1.1 Architecture

**Pattern**: Component-based architecture with React Hooks

```
frontend/
├── src/
│   ├── components/          # UI Components
│   │   ├── TradingDashboard.tsx    # Main orchestrator
│   │   ├── StrategiesPanel.tsx     # Strategy cards
│   │   ├── SignalsPanel.tsx        # Signal feed
│   │   ├── PriceChart.tsx          # Price charts
│   │   ├── QuickTradePanel.tsx     # Trade entry
│   │   ├── PositionsPanel.tsx      # Positions
│   │   ├── RiskManagement.tsx      # Risk metrics
│   │   └── ConnectionStatus.tsx    # Connection health
│   ├── hooks/               # Custom React hooks
│   │   └── useWebSocket.ts         # WebSocket connection
│   ├── services/            # Business logic
│   │   └── websocket.ts            # WebSocket service
│   ├── types/               # TypeScript types
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
└── package.json
```

#### 3.1.2 Key Components

**TradingDashboard.tsx**
- **Purpose**: Main dashboard orchestrator
- **State Management**: React Context for WebSocket data
- **Child Components**: All panels
- **Data Flow**: Receives WebSocket messages → Updates context → Triggers re-renders

**StrategiesPanel.tsx**
- **Purpose**: Display AI strategy cards
- **Input**: Array of strategy signals from WebSocket
- **Output**: Visual strategy cards with confidence scores
- **Update Pattern**: Real-time on signal arrival

**SignalsPanel.tsx**
- **Purpose**: Chronological signal feed
- **Input**: Signal stream from WebSocket
- **State**: Maintains last 100 signals
- **Features**: Auto-scroll, color-coded by direction

**PriceChart.tsx / TradingChart.tsx**
- **Purpose**: Real-time candlestick charts
- **Library**: lightweight-charts
- **Timeframes**: 1m, 5m, 15m, 1h, 4h
- **Performance**: Optimized for 1000+ candles

#### 3.1.3 State Management

**Current**: React Context API + useState/useEffect hooks

**Data Flow**:
```typescript
WebSocket Message → useWebSocket hook → Context Provider → Components
```

**Future Enhancement**: Zustand for complex state
```typescript
// store/signals.ts
export const useSignalsStore = create((set) => ({
  signals: [],
  addSignal: (signal) => set((state) => ({
    signals: [signal, ...state.signals].slice(0, 100)
  }))
}));
```

#### 3.1.4 WebSocket Integration

**File**: `services/websocket.ts`

```typescript
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(url: string, messageHandler: (data: any) => void) {
    this.ws = new WebSocket(url);
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      messageHandler(data);
    };
    this.ws.onerror = () => this.handleReconnect(url, messageHandler);
  }
  
  handleReconnect(url: string, messageHandler: (data: any) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => this.connect(url, messageHandler), 2000);
    }
  }
}
```

---

### 3.2 Node Gateway

**Location**: `node_gateway/`

#### 3.2.1 Architecture

```
node_gateway/
├── src/
│   ├── index.ts                 # Main entry, WebSocket server
│   ├── api/
│   │   └── routes/              # REST API routes (future)
│   ├── websockets/
│   │   ├── ClientManager.ts     # WebSocket client management
│   │   └── MessageBroadcaster.ts
│   ├── brokers/                 # Broker integrations (future)
│   ├── integrations/            # 100+ API connectors (future)
│   └── utils/
│       └── logger.ts
└── package.json
```

#### 3.2.2 WebSocket Server Design

**File**: `src/index.ts`

**Responsibilities**:
1. Host WebSocket server on port 8080
2. Identify connection types (Python backend vs React frontend)
3. Route messages appropriately
4. Broadcast to all frontend clients

**Connection Detection**:
```typescript
ws.on('message', (data) => {
  const message = JSON.parse(data);
  
  // Identify Python backend (sends tick_update, signal_update)
  if (message.type === 'tick_update' || message.type === 'signal_update') {
    console.log('Python backend connected');
    // Broadcast to all frontend clients
    broadcastToFrontend(message);
  }
  
  // Frontend clients (send trade requests, etc.)
  else {
    handleFrontendMessage(message);
  }
});
```

#### 3.2.3 Client Manager

**Purpose**: Manage multiple WebSocket connections

```typescript
class ClientManager {
  private pythonClient: WebSocket | null = null;
  private frontendClients: Set<WebSocket> = new Set();
  
  addFrontendClient(ws: WebSocket) {
    this.frontendClients.add(ws);
    ws.on('close', () => this.frontendClients.delete(ws));
  }
  
  setPythonClient(ws: WebSocket) {
    this.pythonClient = ws;
  }
  
  broadcast(message: any) {
    const data = JSON.stringify(message);
    this.frontendClients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  }
}
```

#### 3.2.4 REST API Design (Planned)

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/strategies` | List all strategies |
| POST | `/api/v1/orders` | Place new order |
| GET | `/api/v1/positions` | Get open positions |
| GET | `/api/v1/signals` | Get historical signals |
| GET | `/api/v1/health` | Health check |

---

### 3.3 IBKR Streaming Service

**Location**: `ibkr_streaming/`

#### 3.3.1 Architecture

```
ibkr_streaming/
├── run.py                  # Main orchestrator
├── tick_stream.py          # IBKR tick streaming
├── candle_engine.py        # Multi-timeframe candles
├── microstructure.py       # Market microstructure
├── ws_push.py              # WebSocket client
├── config.py               # Configuration
├── logger.py               # Logging setup
└── symbols.py              # Symbol definitions
```

#### 3.3.2 Main Orchestrator

**File**: `run.py`

**Flow**:
```python
async def main():
    # 1. Initialize logging
    setup_logging()
    
    # 2. Connect to IBKR
    ibkr_client = IBKRClient()
    await ibkr_client.connect()
    
    # 3. Initialize candle engine
    candle_engine = CandleEngine()
    
    # 4. Initialize strategy manager
    strategy_manager = StrategyManager()
    
    # 5. Initialize WebSocket pusher
    ws_pusher = WebSocketPusher("ws://localhost:8080/ws")
    
    # 6. Start tick streaming
    tick_streamer = TickStreamer(ibkr_client)
    
    # 7. Main loop
    async for tick in tick_streamer.stream():
        # Update candles
        candles = candle_engine.update(tick)
        
        # Process through strategies
        signals = strategy_manager.process_tick(tick.symbol, tick.price)
        
        # Push to Node Gateway
        await ws_pusher.push_tick(tick)
        if candles:
            await ws_pusher.push_candles(candles)
        if signals:
            await ws_pusher.push_signals(signals)
```

#### 3.3.3 Tick Streaming

**File**: `tick_stream.py`

**Class**: `TickStreamer`

```python
class TickStreamer:
    def __init__(self, ibkr_client):
        self.client = ibkr_client
        self.subscribed_symbols = []
    
    def subscribe(self, symbols: List[str]):
        for symbol in symbols:
            contract = self._create_contract(symbol)
            self.client.reqMktData(reqId, contract, "", False, False, [])
    
    async def stream(self):
        """Generator yielding tick data"""
        while True:
            tick = await self._get_next_tick()
            yield Tick(
                symbol=tick.symbol,
                bid=tick.bid,
                ask=tick.ask,
                mid=(tick.bid + tick.ask) / 2,
                spread=tick.ask - tick.bid,
                timestamp=tick.timestamp
            )
```

#### 3.3.4 Candle Engine

**File**: `candle_engine.py`

**Purpose**: Build multi-timeframe candles from ticks

```python
class CandleEngine:
    def __init__(self):
        self.candles = {
            '1m': CandleBuilder(60),
            '5m': CandleBuilder(300),
            '15m': CandleBuilder(900),
            '1h': CandleBuilder(3600),
            '4h': CandleBuilder(14400)
        }
    
    def update(self, tick: Tick) -> List[Candle]:
        completed_candles = []
        for timeframe, builder in self.candles.items():
            candle = builder.add_tick(tick)
            if candle:  # Candle is complete
                completed_candles.append(candle)
        return completed_candles

class CandleBuilder:
    def __init__(self, period_seconds: int):
        self.period = period_seconds
        self.current_candle = None
    
    def add_tick(self, tick: Tick) -> Optional[Candle]:
        candle_start = (tick.timestamp // self.period) * self.period
        
        if not self.current_candle:
            self.current_candle = Candle(
                open=tick.mid, high=tick.mid,
                low=tick.mid, close=tick.mid,
                timestamp=candle_start
            )
        elif tick.timestamp >= candle_start + self.period:
            # Complete current candle
            completed = self.current_candle
            self.current_candle = Candle(...)
            return completed
        else:
            # Update current candle
            self.current_candle.high = max(self.current_candle.high, tick.mid)
            self.current_candle.low = min(self.current_candle.low, tick.mid)
            self.current_candle.close = tick.mid
```

---

### 3.4 AI Core (Strategy Engine)

**Location**: `ai_core/strategy_engine/`

#### 3.4.1 Architecture

```
ai_core/strategy_engine/
├── strategy_manager.py      # Orchestrates all strategies
├── signal_router.py         # Routes signals to consumers
├── core/
│   ├── feature_engine.py        # Computes technical indicators
│   └── multi_timeframe_feature_engine.py  # M5/M15 feature engine
├── strategies/
│   └── apex_strategy.py     # Apex V1: Multi-timeframe strategy
└── models/                  # Data models
```

#### 3.4.2 Strategy Manager

**File**: `strategy_manager.py`

```python
class StrategyManager:
    def __init__(self):
        self.strategies = []
        self.feature_engine = FeatureEngine()
        self.signal_router = SignalRouter()
        
        # Register strategies
        self.register_strategy(SMAStrategy())
        self.register_strategy(RSIStrategy())
    
    def register_strategy(self, strategy: BaseStrategy):
        self.strategies.append(strategy)
    
    def process_tick(self, symbol: str, price: float) -> List[Signal]:
        # Update features
        self.feature_engine.update_price(symbol, price)
        
        # Execute all strategies
        all_signals = []
        for strategy in self.strategies:
            features = self.feature_engine.get_features(symbol)
            signals = strategy.generate_signals(symbol, features)
            all_signals.extend(signals)
        
        # Broadcast signals
        if all_signals:
            self.signal_router.broadcast_signals(all_signals)
        
        return all_signals
```

#### 3.4.3 Feature Engine

**File**: `feature_engine.py`

**Purpose**: Compute real-time technical indicators

```python
class FeatureEngine:
    def __init__(self):
        self.price_history = defaultdict(lambda: deque(maxlen=200))
    
    def update_price(self, symbol: str, price: float):
        self.price_history[symbol].append(price)
    
    def get_features(self, symbol: str) -> dict:
        prices = np.array(self.price_history[symbol])
        
        return {
            'sma_20': self._sma(prices, 20),
            'sma_50': self._sma(prices, 50),
            'rsi_14': self._rsi(prices, 14),
            'atr_14': self._atr(prices, 14),
            'momentum': prices[-1] - prices[-10] if len(prices) >= 10 else 0
        }
    
    def _sma(self, prices, period):
        return np.mean(prices[-period:]) if len(prices) >= period else None
    
    def _rsi(self, prices, period):
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        return 100 - (100 / (1 + rs))
```

#### 3.4.4 Base Strategy

**File**: `strategies/base_strategy.py`

```python
class BaseStrategy(ABC):
    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        self.last_signal = None
    
    @abstractmethod
    def generate_signals(self, symbol: str, features: dict) -> List[Signal]:
        """Generate trading signals based on features"""
        pass
    
    def create_signal(self, symbol: str, direction: str, 
                      confidence: float, reason: str) -> Signal:
        return Signal(
            symbol=symbol,
            signal=direction,
            strategy_id=self.strategy_id,
            confidence=confidence,
            reason=reason,
            timestamp=int(time.time() * 1000)
        )
```

#### 3.4.5 SMA Crossover Strategy

**File**: `strategies/sma_crossover.py`

```python
class SMAStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("SMA_CROSS")
        self.prev_sma20 = None
        self.prev_sma50 = None
    
    def generate_signals(self, symbol: str, features: dict) -> List[Signal]:
        sma20 = features.get('sma_20')
        sma50 = features.get('sma_50')
        
        if not sma20 or not sma50:
            return []
        
        signals = []
        
        # Bullish crossover
        if self.prev_sma20 and self.prev_sma50:
            if self.prev_sma20 <= self.prev_sma50 and sma20 > sma50:
                signals.append(self.create_signal(
                    symbol=symbol,
                    direction="BUY",
                    confidence=0.72,
                    reason="SMA20 crossed above SMA50"
                ))
            
            # Bearish crossover
            elif self.prev_sma20 >= self.prev_sma50 and sma20 < sma50:
                signals.append(self.create_signal(
                    symbol=symbol,
                    direction="SELL",
                    confidence=0.72,
                    reason="SMA20 crossed below SMA50"
                ))
        
        self.prev_sma20 = sma20
        self.prev_sma50 = sma50
        
        return signals
```

#### 3.4.6 Signal Router

**File**: `signal_router.py`

```python
class SignalRouter:
    def __init__(self):
        self.ws_pusher = None  # Set by ibkr_streaming.run
    
    def set_websocket_pusher(self, ws_pusher):
        self.ws_pusher = ws_pusher
    
    async def broadcast_signals(self, signals: List[Signal]):
        if self.ws_pusher:
            await self.ws_pusher.push_signals(signals)
        else:
            logger.warning("No WebSocket pusher configured")
```

---

## 4. Data Design

### 4.1 Data Models

#### 4.1.1 Tick

```python
@dataclass
class Tick:
    symbol: str
    bid: float
    ask: float
    mid: float
    spread: float
    timestamp: int  # Unix timestamp in milliseconds
```

#### 4.1.2 Candle

```python
@dataclass
class Candle:
    symbol: str
    timeframe: str  # '1m', '5m', '15m', '1h', '4h'
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: int
```

#### 4.1.3 Signal

```python
@dataclass
class Signal:
    symbol: str
    signal: str  # 'BUY', 'SELL'
    strategy_id: str
    confidence: float  # 0.0 to 1.0
    reason: str
    timestamp: int
    price: Optional[float] = None
```

#### 4.1.4 Order (Future)

```python
@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # 'BUY', 'SELL'
    quantity: float
    order_type: str  # 'MARKET', 'LIMIT', 'STOP'
    price: Optional[float]
    status: str  # 'PENDING', 'FILLED', 'CANCELLED', 'REJECTED'
    created_at: int
    filled_at: Optional[int]
```

### 4.2 Database Schema (Planned)

#### 4.2.1 TimescaleDB Hypertables

```sql
-- Signals table
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    signal VARCHAR(4) NOT NULL,
    strategy_id VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4),
    reason TEXT,
    price DECIMAL(12,5),
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('signals', 'timestamp');
CREATE INDEX idx_signals_symbol ON signals(symbol, timestamp DESC);
CREATE INDEX idx_signals_strategy ON signals(strategy_id, timestamp DESC);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID REFERENCES signals(id),
    symbol VARCHAR(10) NOT NULL,
    side VARCHAR(4) NOT NULL,
    quantity DECIMAL(12,5),
    entry_price DECIMAL(12,5),
    exit_price DECIMAL(12,5),
    pnl DECIMAL(12,2),
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ,
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('trades', 'entry_time');

-- Ticks table (optional, high volume)
CREATE TABLE ticks (
    symbol VARCHAR(10) NOT NULL,
    bid DECIMAL(12,5),
    ask DECIMAL(12,5),
    mid DECIMAL(12,5),
    spread DECIMAL(8,5),
    timestamp TIMESTAMPTZ NOT NULL
);

SELECT create_hypertable('ticks', 'timestamp');
CREATE INDEX idx_ticks_symbol ON ticks(symbol, timestamp DESC);

-- Candles table
CREATE TABLE candles (
    symbol VARCHAR(10) NOT NULL,
    timeframe VARCHAR(3) NOT NULL,
    open DECIMAL(12,5),
    high DECIMAL(12,5),
    low DECIMAL(12,5),
    close DECIMAL(12,5),
    volume BIGINT,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (symbol, timeframe, timestamp)
);

SELECT create_hypertable('candles', 'timestamp');
```

### 4.3 Message Formats

#### 4.3.1 WebSocket Message Types

**Tick Update**:
```json
{
  "type": "tick_update",
  "data": {
    "symbol": "EURUSD",
    "bid": 1.09450,
    "ask": 1.09452,
    "mid": 1.09451,
    "spread": 0.00002,
    "timestamp": 1704234567890
  }
}
```

**Candle Update**:
```json
{
  "type": "candle_update",
  "data": {
    "symbol": "EURUSD",
    "timeframe": "1m",
    "open": 1.09450,
    "high": 1.09480,
    "low": 1.09440,
    "close": 1.09475,
    "volume": 1000,
    "timestamp": 1704234600000
  }
}
```

**Signal Update**:
```json
{
  "type": "signal_update",
  "data": [
    {
      "symbol": "EURUSD",
      "signal": "BUY",
      "strategy_id": "SMA_CROSS",
      "confidence": 0.72,
      "reason": "SMA20 crossed above SMA50",
      "timestamp": 1704234567890,
      "price": 1.09451
    }
  ]
}
```

---

## 5. Interface Design

### 5.1 WebSocket Interface

**Endpoint**: `ws://localhost:8080/ws`

**Protocol**: RFC 6455 (WebSocket)

**Message Format**: JSON

**Connection Flow**:
```
Client → Connect to ws://localhost:8080/ws
Client ← Connection established
Client → Send heartbeat every 30s
Server → Broadcast tick_update, candle_update, signal_update
Client ← Receive updates
```

### 5.2 IBKR API Interface

**Connection**: TCP Socket to localhost:7497 (paper) or localhost:7496 (live)

**Library**: `ib_async` (Interactive Brokers Python Async API)

**Key Methods**:
- `reqMktData()`: Subscribe to market data
- `reqAccountUpdates()`: Subscribe to account updates
- `placeOrder()`: Place new order
- `cancelOrder()`: Cancel order

### 5.3 REST API Interface (Planned)

**Base URL**: `http://localhost:8080/api/v1`

**Authentication**: JWT tokens (future)

**Endpoints**:

```
GET    /api/v1/strategies          - List all strategies
POST   /api/v1/strategies/:id/toggle - Enable/disable strategy
GET    /api/v1/signals             - Get historical signals
GET    /api/v1/signals/:id         - Get signal details
POST   /api/v1/orders              - Place new order
GET    /api/v1/orders              - List orders
GET    /api/v1/orders/:id          - Get order details
DELETE /api/v1/orders/:id          - Cancel order
GET    /api/v1/positions           - Get open positions
GET    /api/v1/account             - Get account metrics
GET    /api/v1/health              - Health check
```

---

## 6. Deployment Architecture

### 6.1 Development Environment

```
┌─────────────────────────────────────┐
│   Developer Machine (macOS/Linux)  │
│                                     │
│  Terminal 1: Frontend (Vite)       │
│  → cd frontend && npm run dev       │
│  → http://localhost:5173            │
│                                     │
│  Terminal 2: Node Gateway           │
│  → cd node_gateway && npm run dev   │
│  → http://localhost:8080            │
│                                     │
│  Terminal 3: IBKR Streaming         │
│  → python -m ibkr_streaming.run     │
│                                     │
│  Terminal 4: IBKR TWS/Gateway       │
│  → Running on localhost:7497        │
└─────────────────────────────────────┘
```

### 6.2 Docker Compose Deployment

```yaml
version: "3.9"

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: fxharry
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  node_gateway:
    build: ./node_gateway
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      DB_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/fxharry
    depends_on:
      - redis
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - node_gateway
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
```

### 6.3 Production Architecture (Kubernetes - Planned)

```
                            ┌──────────────┐
                            │  Ingress     │
                            │  Controller  │
                            └──────┬───────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼────┐  ┌──────▼────┐  ┌─────▼──────┐
            │  Frontend  │  │   Node    │  │   API      │
            │  Service   │  │  Gateway  │  │  Service   │
            │  (3 pods)  │  │ (3 pods)  │  │  (2 pods)  │
            └────────────┘  └─────┬─────┘  └────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼────┐  ┌─────▼──────┐  ┌──▼──────────┐
            │ PostgreSQL │  │   Redis    │  │  AI Core    │
            │  StatefulSet│  │ (Cluster) │  │  (3 pods)   │
            └────────────┘  └────────────┘  └─────────────┘
```

---

## Appendices

### A. File Structure Reference

```
fxharry-main/
├── frontend/                 # React dashboard
├── node_gateway/             # Node.js gateway
├── ibkr_streaming/           # IBKR data service
├── ai_core/                  # Python AI engine
│   ├── strategy_engine/      # Trading strategies
│   ├── ml_engine/            # ML models
│   ├── genai/                # LLM integration
│   ├── risk_manager/         # Risk management
│   └── backtesting/          # Backtesting
├── cpp_engine/               # C++ execution (future)
├── shared/                   # Cross-language schemas
├── infra/                    # Infrastructure configs
├── tests/                    # Test suite
├── docs/                     # Documentation
│   ├── SRS.md                # Software Requirements Spec
│   ├── SDD.md                # Software Design Document
│   └── TECHNOLOGY_REVIEW.md  # Tech stack analysis
├── docker-compose.yml        # Development deployment
└── README.md                 # Project overview
```

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-02 | Rizwan Beg | Initial SDD creation |

---

**END OF SOFTWARE DESIGN DOCUMENT**
