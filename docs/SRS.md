# Software Requirements Specification (SRS)
## FXHarry - QuantX AI-Powered Trading System

**Document Version**: 1.0  
**Date**: January 2, 2026  
**Project**: FXHarry (QuantX)  
**Document Owner**: Rizwan Beg

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features and Requirements](#3-system-features-and-requirements)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Appendices](#6-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a complete description of all functions and specifications of the FXHarry (QuantX) AI-Powered Trading System. This document is intended for:

- Development team members
- Project stakeholders
- System architects
- Quality assurance engineers
- Future maintainers and contributors

### 1.2 Document Conventions

- **SHALL/MUST**: Mandatory requirement
- **SHOULD**: Highly desirable requirement
- **MAY**: Optional requirement
- **Priority Levels**: 
  - **P0**: Critical - Core functionality
  - **P1**: High - Important features
  - **P2**: Medium - Enhanced features
  - **P3**: Low - Nice-to-have features

### 1.3 Intended Audience

- **Solo Quant Traders**: Individual traders seeking institutional-grade trading systems
- **AI Researchers**: Researchers developing ML/DL/RL strategies
- **Algorithm Trading Enthusiasts**: Developers building automated trading systems
- **Institutional Developers**: Teams building production trading infrastructure

### 1.4 Project Scope

FXHarry (QuantX) is a next-generation, full-stack quantitative trading platform designed to provide:

- **Real-time forex market execution** via Interactive Brokers
- **AI-powered trading signals** using ML, DL, and RL algorithms
- **Multi-agent strategy system** with hybrid rule-based and AI strategies
- **Professional trading dashboard** with real-time updates
- **100+ API integration capability** for brokers, news, and data sources
- **GenAI-driven strategy reasoning** using LLMs
- **Optional C++ execution engine** for low-latency requirements

**Key Differentiators**:
- Institutional-grade architecture maintainable by a single person
- Modular, extensible design for unlimited strategy and API plugins
- Real-time multi-timeframe analysis
- AI-first design philosophy

### 1.5 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **API** | Application Programming Interface |
| **AI** | Artificial Intelligence |
| **ATR** | Average True Range |
| **DL** | Deep Learning |
| **EMS** | Execution Management System |
| **GenAI** | Generative AI |
| **gRPC** | Google Remote Procedure Call |
| **IBKR** | Interactive Brokers |
| **LLM** | Large Language Model |
| **MCP** | Model Context Protocol |
| **ML** | Machine Learning |
| **P&L** | Profit and Loss |
| **RL** | Reinforcement Learning |
| **RSI** | Relative Strength Index |
| **SMA** | Simple Moving Average |
| **TWS** | Trader Workstation (IBKR's trading platform) |
| **UI** | User Interface |
| **VaR** | Value at Risk |
| **WebSocket** | Full-duplex communication protocol |

### 1.6 References

- **TECHNOLOGY_REVIEW.md**: Technical architecture analysis
- **fxharry_project_overview.md.resolved**: Current project status
- **README.md**: Project overview and architecture
- Interactive Brokers API Documentation
- React 18 Documentation
- Node.js Documentation
- Python 3.10+ Documentation

---

## 2. Overall Description

### 2.1 Product Perspective

FXHarry is a standalone, full-stack trading system that integrates with external brokers and data providers. The system architecture consists of:

```
┌─────────────────────────────────────────────────────────────┐
│                   External Systems                          │
│  (IBKR, TradingView, Polygon, News APIs, LLM Services)     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Node.js Gateway                            │
│          (API Hub, WebSocket Server, I/O Engine)            │
└──────────────────┬───────────────────┬──────────────────────┘
                   │                   │
        ┌──────────▼────────┐   ┌─────▼──────────┐
        │   Python AI Core  │   │ React Frontend │
        │ (ML/DL/RL/GenAI)  │   │   Dashboard    │
        └───────────────────┘   └────────────────┘
                   │
        ┌──────────▼────────┐
        │  Optional C++     │
        │  Execution Engine │
        └───────────────────┘
```

### 2.2 Product Features

#### 2.2.1 Core Features (Implemented)

1. **Real-Time Market Data Integration**
   - Live tick streaming from Interactive Brokers
   - Multi-timeframe candle generation (1m, 5m, 15m, 1h, 4h)
   - Market microstructure analysis

2. **AI Strategy Engine**
   - Multiple trading strategies (SMA Crossover, RSI Reversal, Demo)
   - Real-time technical indicator computation
   - Signal generation with confidence scores
   - Strategy signal routing to frontend

3. **Professional Trading Dashboard**
   - Real-time price charts
   - Live strategy cards with AI recommendations
   - Signal feed panel
   - Quick trade interface
   - Connection status monitoring

4. **Full-Stack Communication**
   - WebSocket-based real-time communication
   - Dual connection handling (backend + frontend)
   - Auto-reconnection capabilities

#### 2.2.2 Planned Features

1. **100+ API Integration System**
2. **Advanced ML Models** (LSTM, Transformers, RL Agents)
3. **GenAI Integration** (LLM reasoning, sentiment analysis)
4. **Trade Execution Management**
5. **Risk Management System**
6. **Historical Data Warehouse**
7. **Production Infrastructure** (Kubernetes, monitoring)
8. **C++ Low-Latency Engine**

### 2.3 User Classes and Characteristics

| User Class | Technical Expertise | Primary Use Case |
|------------|-------------------|------------------|
| **Quant Trader** | High | Developing and testing trading strategies |
| **ML Researcher** | Very High | Training and deploying ML/RL models |
| **Day Trader** | Medium | Executing trades based on AI signals |
| **System Administrator** | High | Deploying and maintaining infrastructure |
| **Strategy Analyst** | Medium-High | Analyzing strategy performance |

### 2.4 Operating Environment

**Development Environment**:
- **OS**: macOS, Linux, Windows (WSL2)
- **Frontend**: Modern web browsers (Chrome, Firefox, Safari, Edge)
- **Backend**: Python 3.10+, Node.js 18+
- **Broker**: Interactive Brokers TWS or IB Gateway

**Production Environment** (Future):
- **Container Platform**: Docker, Kubernetes
- **Database**: PostgreSQL with TimescaleDB extension
- **Message Queue**: Redis Pub/Sub or Apache Kafka
- **Monitoring**: Prometheus + Grafana
- **Cloud Providers**: AWS, GCP, or Azure

### 2.5 Design and Implementation Constraints

1. **Real-Time Performance**: System MUST process market ticks with < 100ms latency
2. **Broker Limitations**: Interactive Brokers API rate limits and connection requirements
3. **Language Constraints**: Python for AI/ML (ecosystem requirement), Node.js for I/O, React for frontend
4. **Data Persistence**: Currently no database (planned enhancement)
5. **Message Reliability**: Currently no message queue (planned enhancement)
6. **Scalability**: Single-server architecture (horizontal scaling planned)

### 2.6 Assumptions and Dependencies

**Assumptions**:
- User has active Interactive Brokers account (paper or live)
- IBKR TWS or IB Gateway is running and accessible
- User has basic understanding of forex trading
- Network connectivity is stable

**Dependencies**:
- Interactive Brokers API (ibapi)
- Node.js runtime environment
- Python runtime environment
- Modern web browser with WebSocket support
- External data providers (IBKR for market data)

---

## 3. System Features and Requirements

### 3.1 Market Data Management

#### 3.1.1 Real-Time Tick Streaming

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL stream real-time tick data from Interactive Brokers for subscribed forex symbols.

**Functional Requirements**:

- **FR-MD-001**: System SHALL connect to IBKR TWS/Gateway on configurable port (default 7497)
- **FR-MD-002**: System SHALL subscribe to forex symbols (EURUSD, GBPUSD, etc.)
- **FR-MD-003**: System SHALL capture tick data including bid, ask, mid price, spread, and timestamp
- **FR-MD-004**: System SHALL normalize tick data into standardized format
- **FR-MD-005**: System SHALL handle connection drops with automatic reconnection
- **FR-MD-006**: System SHALL log all tick data with microsecond precision timestamps
- **FR-MD-007**: System SHALL support at minimum 10 concurrent symbol subscriptions
- **FR-MD-008**: System SHALL push tick data to Node Gateway via WebSocket

**Non-Functional Requirements**:
- Tick processing latency: < 10ms
- Connection recovery time: < 5 seconds
- Tick data accuracy: 100% (no data loss during normal operation)

#### 3.1.2 Multi-Timeframe Candle Generation

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL generate and maintain candles across multiple timeframes from tick data.

**Functional Requirements**:

- **FR-MD-009**: System SHALL generate 1-minute candles from tick data
- **FR-MD-010**: System SHALL generate 5-minute candles
- **FR-MD-011**: System SHALL generate 15-minute candles
- **FR-MD-012**: System SHALL generate 1-hour candles
- **FR-MD-013**: System SHALL generate 4-hour candles
- **FR-MD-014**: Each candle SHALL contain: open, high, low, close, volume, timestamp
- **FR-MD-015**: System SHALL update candles in real-time as ticks arrive
- **FR-MD-016**: System SHALL broadcast completed candles to downstream consumers
- **FR-MD-017**: System SHALL maintain candle history for at least 200 candles per timeframe

**Non-Functional Requirements**:
- Candle calculation accuracy: 100%
- Memory footprint: < 100MB per symbol
- Candle close event latency: < 50ms

#### 3.1.3 Market Microstructure Analysis

**Priority**: P1 (High)  
**Status**: ✅ Implemented (Basic)

**Functional Requirements**:

- **FR-MD-018**: System SHALL calculate real-time spread
- **FR-MD-019**: System SHALL track bid-ask dynamics
- **FR-MD-020**: System MAY calculate order flow metrics (future)
- **FR-MD-021**: System MAY detect liquidity conditions (future)

### 3.2 AI Strategy Engine

#### 3.2.1 Strategy Management

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL manage multiple trading strategies and coordinate their execution.

**Functional Requirements**:

- **FR-STR-001**: System SHALL support pluggable strategy architecture
- **FR-STR-002**: Each strategy SHALL be independently configurable
- **FR-STR-003**: System SHALL execute all active strategies on every price update
- **FR-STR-004**: System SHALL aggregate signals from multiple strategies
- **FR-STR-005**: System SHALL manage strategy lifecycle (enable/disable)
- **FR-STR-006**: System SHALL log all strategy executions and decisions
- **FR-STR-007**: System SHALL support at minimum 20 concurrent strategies
- **FR-STR-008**: System SHALL isolate strategy failures (one failing strategy SHALL NOT crash others)

#### 3.2.2 Feature Engineering

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL compute real-time technical indicators for strategy consumption.

**Functional Requirements**:

- **FR-FE-001**: System SHALL calculate Simple Moving Average (SMA) for configurable periods
- **FR-FE-002**: System SHALL calculate Relative Strength Index (RSI-14)
- **FR-FE-003**: System SHALL calculate Average True Range (ATR-14)
- **FR-FE-004**: System SHALL calculate momentum indicators
- **FR-FE-005**: System SHALL maintain sufficient price history for indicator calculation (minimum 200 periods)
- **FR-FE-006**: System SHALL update indicators on every price tick
- **FR-FE-007**: System SHALL provide indicator values with < 5ms latency
- **FR-FE-008**: System SHALL support addition of new indicators without core code changes

**Supported Indicators**:
- SMA (20, 50, 100, 200 periods)
- RSI (14 period)
- ATR (14 period)
- Momentum
- (Future: MACD, Bollinger Bands, Ichimoku, custom ML features)

#### 3.2.3 Signal Generation

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL generate trading signals with metadata and confidence scores.

**Functional Requirements**:

- **FR-SIG-001**: Each signal SHALL include: symbol, direction (BUY/SELL), strategy_id, confidence, reason, timestamp
- **FR-SIG-002**: Signal confidence SHALL be normalized between 0.0 and 1.0
- **FR-SIG-003**: Signal reason SHALL be human-readable explanation
- **FR-SIG-004**: System SHALL timestamp signals with millisecond precision
- **FR-SIG-005**: System SHALL broadcast signals immediately upon generation (< 50ms)
- **FR-SIG-006**: System SHALL deduplicate identical consecutive signals from same strategy
- **FR-SIG-007**: System SHALL rate-limit signals to prevent flooding (max 10 signals/second per strategy)
- **FR-SIG-008**: System SHALL persist signals for historical analysis (future)

**Signal Format**:
```json
{
  "symbol": "EURUSD",
  "signal": "BUY" | "SELL",
  "strategy_id": "SMA_CROSS",
  "confidence": 0.72,
  "reason": "SMA20 crossed above SMA50",
  "timestamp": 1704234567890,
  "price": 1.0950
}
```

#### 3.2.4 Strategy Types

**Priority**: P0-P2 (Mixed)

**Functional Requirements**:

- **FR-STR-009** [P0, ✅]: System SHALL support rule-based strategies (SMA, RSI, MACD)
- **FR-STR-010** [P1, 🔄]: System SHALL support ML-based strategies (LSTM, Transformers)
- **FR-STR-011** [P2, ❌]: System SHALL support RL-based strategies (PPO, SAC, DQN)
- **FR-STR-012** [P2, ❌]: System SHALL support hybrid strategies (AI + statistical + GenAI)
- **FR-STR-013** [P2, ❌]: System SHALL support sentiment/NLP strategies (FinBERT, GPT)
- **FR-STR-014** [P2, ❌]: System SHALL support GenAI agent strategies (LLM-driven reasoning)

**Current Implemented Strategies**:
1. **SMA Crossover**: Detects SMA20/SMA50 crossovers
2. **RSI Reversal**: Identifies overbought/oversold conditions
3. **Demo Strategy**: Testing and demonstration

### 3.3 Trading Dashboard (Frontend)

#### 3.3.1 User Interface

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL provide a professional, real-time trading dashboard.

**Functional Requirements**:

- **FR-UI-001**: Dashboard SHALL display real-time price charts
- **FR-UI-002**: Dashboard SHALL display active strategy cards with confidence scores
- **FR-UI-003**: Dashboard SHALL display live signal feed
- **FR-UI-004**: Dashboard SHALL provide quick trade panel
- **FR-UI-005**: Dashboard SHALL display portfolio positions (future)
- **FR-UI-006**: Dashboard SHALL display risk metrics (future)
- **FR-UI-007**: Dashboard SHALL show connection status indicators
- **FR-UI-008**: Dashboard SHALL support responsive design (desktop, tablet)
- **FR-UI-009**: Dashboard SHALL update in real-time (< 100ms from signal generation)
- **FR-UI-010**: Dashboard SHALL maintain 60 FPS during updates

#### 3.3.2 Price Charts

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Functional Requirements**:

- **FR-CHT-001**: System SHALL display candlestick charts
- **FR-CHT-002**: Charts SHALL support multiple timeframes (1m, 5m, 15m, 1h, 4h)
- **FR-CHT-003**: Charts SHALL update in real-time as candles complete
- **FR-CHT-004**: Charts SHALL support zoom and pan
- **FR-CHT-005**: Charts SHALL display volume (if available)
- **FR-CHT-006**: Charts MAY display technical indicators (overlays)
- **FR-CHT-007**: Charts SHALL be performant with 1000+ candles

#### 3.3.3 Strategy Cards

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Functional Requirements**:

- **FR-SC-001**: Each strategy SHALL have a dedicated card
- **FR-SC-002**: Cards SHALL display strategy name and ID
- **FR-SC-003**: Cards SHALL show current signal (BUY/SELL/NEUTRAL)
- **FR-SC-004**: Cards SHALL display confidence percentage
- **FR-SC-005**: Cards SHALL show last update timestamp
- **FR-SC-006**: Cards SHALL use color coding (green=BUY, red=SELL, gray=NEUTRAL)
- **FR-SC-007**: Cards SHALL update immediately when new signals arrive

#### 3.3.4 Signal Feed

**Priority**: P1 (High)  
**Status**: ✅ Implemented

**Functional Requirements**:

- **FR-SF-001**: System SHALL display chronological signal feed
- **FR-SF-002**: Feed SHALL show signal timestamp, symbol, direction, strategy, confidence
- **FR-SF-003**: Feed SHALL maintain history of at least 100 signals
- **FR-SF-004**: Feed SHALL auto-scroll to show latest signals
- **FR-SF-005**: Feed SHALL support filtering by symbol, strategy, or direction (future)
- **FR-SF-006**: Feed SHALL support export to CSV (future)

### 3.4 Communication Infrastructure

#### 3.4.1 WebSocket Communication

**Priority**: P0 (Critical)  
**Status**: ✅ Implemented

**Description**: 
The system SHALL use WebSocket for real-time bidirectional communication.

**Functional Requirements**:

- **FR-WS-001**: Node Gateway SHALL host WebSocket server on port 8080
- **FR-WS-002**: System SHALL support multiple concurrent WebSocket connections
- **FR-WS-003**: System SHALL identify connection type (Python backend vs React frontend)
- **FR-WS-004**: System SHALL broadcast messages to appropriate client groups
- **FR-WS-005**: System SHALL implement heartbeat/ping-pong for connection health
- **FR-WS-006**: System SHALL auto-reconnect on connection loss
- **FR-WS-007**: System SHALL queue messages during disconnection (future with Redis)
- **FR-WS-008**: System SHALL support message compression for large payloads

**Message Types**:
- `tick_update`: Market tick data
- `candle_update`: Completed candles
- `signal_update`: Trading signals
- `account_metrics`: Account metrics (future)
- `position_update`: Position changes (future)
- `connection_status`: Connection state changes

#### 3.4.2 REST API

**Priority**: P1 (High)  
**Status**: 🔄 Partial

**Functional Requirements**:

- **FR-API-001**: System SHALL provide REST API for non-real-time operations
- **FR-API-002**: API SHALL support trade execution endpoints (future)
- **FR-API-003**: API SHALL provide historical data queries (future)
- **FR-API-004**: API SHALL provide strategy configuration endpoints (future)
- **FR-API-005**: API SHALL implement authentication (future)
- **FR-API-006**: API SHALL implement rate limiting (future)
- **FR-API-007**: API SHALL return standardized error responses

#### 3.4.3 gRPC Communication

**Priority**: P2 (Medium)  
**Status**: ❌ Configured but not used

**Functional Requirements**:

- **FR-GRPC-001**: System MAY implement gRPC for Python ↔ Node communication
- **FR-GRPC-002**: gRPC SHALL use Protobuf for message serialization
- **FR-GRPC-003**: gRPC SHALL provide better performance than WebSocket for high-volume scenarios
- **FR-GRPC-004**: System SHALL maintain shared .proto schema definitions

**Decision**: Currently using WebSocket; gRPC planned for future high-volume optimization

### 3.5 Trade Execution (Planned)

#### 3.5.1 Order Management

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Description**: 
The system SHALL manage trade execution and order lifecycle.

**Functional Requirements**:

- **FR-ORD-001**: System SHALL support market orders
- **FR-ORD-002**: System SHALL support limit orders
- **FR-ORD-003**: System SHALL support stop-loss orders
- **FR-ORD-004**: System SHALL support take-profit orders
- **FR-ORD-005**: System SHALL validate orders before submission
- **FR-ORD-006**: System SHALL track order status (pending, filled, cancelled, rejected)
- **FR-ORD-007**: System SHALL provide order execution confirmation
- **FR-ORD-008**: System SHALL implement order timeout handling
- **FR-ORD-009**: System SHALL log all order activities
- **FR-ORD-010**: System SHALL support order modification and cancellation

#### 3.5.2 Position Management

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-POS-001**: System SHALL track open positions
- **FR-POS-002**: System SHALL calculate real-time P&L for each position
- **FR-POS-003**: System SHALL display position entry price, current price, and P&L
- **FR-POS-004**: System SHALL support position closing (full or partial)
- **FR-POS-005**: System SHALL track position history
- **FR-POS-006**: System SHALL calculate aggregate portfolio P&L

### 3.6 Risk Management (Planned)

#### 3.6.1 Position Sizing

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-RISK-001**: System SHALL implement position sizing algorithms
- **FR-RISK-002**: System SHALL support fixed fractional position sizing
- **FR-RISK-003**: System SHALL support Kelly Criterion sizing
- **FR-RISK-004**: System SHALL enforce maximum position size limits
- **FR-RISK-005**: System SHALL calculate risk per trade based on account size

#### 3.6.2 Risk Metrics

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-RISK-006**: System SHALL calculate portfolio Value at Risk (VaR)
- **FR-RISK-007**: System SHALL calculate Sharpe ratio
- **FR-RISK-008**: System SHALL track maximum drawdown
- **FR-RISK-009**: System SHALL monitor correlation between positions
- **FR-RISK-010**: System SHALL provide risk alerts when limits are breached

#### 3.6.3 Stop-Loss Management

**Priority**: P0 (Critical)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-RISK-011**: System SHALL support automatic stop-loss placement
- **FR-RISK-012**: System SHALL support trailing stop-loss
- **FR-RISK-013**: System SHALL enforce maximum loss per trade
- **FR-RISK-014**: System SHALL enforce maximum daily loss limit

### 3.7 Machine Learning Integration (Planned)

#### 3.7.1 Model Training

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-ML-001**: System SHALL support LSTM model training
- **FR-ML-002**: System SHALL support Transformer model training
- **FR-ML-003**: System SHALL support custom PyTorch model architectures
- **FR-ML-004**: System SHALL implement automated hyperparameter tuning
- **FR-ML-005**: System SHALL track model training metrics
- **FR-ML-006**: System SHALL version trained models

#### 3.7.2 Model Deployment

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-ML-007**: System SHALL support real-time model inference
- **FR-ML-008**: System SHALL load models dynamically without restart
- **FR-ML-009**: System SHALL support A/B testing between models
- **FR-ML-010**: System SHALL monitor model prediction latency
- **FR-ML-011**: System SHALL detect model degradation
- **FR-ML-012**: System SHALL support model rollback

#### 3.7.3 Reinforcement Learning

**Priority**: P2 (Medium)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-RL-001**: System SHALL support PPO agent training
- **FR-RL-002**: System SHALL support SAC agent training
- **FR-RL-003**: System SHALL support DQN agent training
- **FR-RL-004**: System SHALL provide trading environment for RL agents
- **FR-RL-005**: System SHALL support multi-agent coordination
- **FR-RL-006**: System SHALL implement reward shaping for trading objectives

### 3.8 GenAI Integration (Planned)

#### 3.8.1 LLM-Based Reasoning

**Priority**: P2 (Medium)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-GENAI-001**: System SHALL integrate LLM for strategy reasoning
- **FR-GENAI-002**: System SHALL generate natural language explanations for signals
- **FR-GENAI-003**: System SHALL use LLM for market regime detection
- **FR-GENAI-004**: System SHALL support multi-turn agent conversations (MCP)
- **FR-GENAI-005**: System SHALL implement prompt engineering for trading context

#### 3.8.2 Sentiment Analysis

**Priority**: P2 (Medium)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-SENT-001**: System SHALL collect news data from configured sources
- **FR-SENT-002**: System SHALL analyze news sentiment using FinBERT
- **FR-SENT-003**: System SHALL aggregate sentiment scores by symbol
- **FR-SENT-004**: System SHALL integrate sentiment into trading signals
- **FR-SENT-005**: System SHALL track sentiment changes over time

### 3.9 Data Persistence (Planned)

#### 3.9.1 Database Requirements

**Priority**: P0 (Critical for production)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-DB-001**: System SHALL persist all trading signals
- **FR-DB-002**: System SHALL persist all executed trades
- **FR-DB-003**: System SHALL persist tick data (optional, high volume)
- **FR-DB-004**: System SHALL persist candle data
- **FR-DB-005**: System SHALL persist account metrics history
- **FR-DB-006**: System SHALL support time-series queries
- **FR-DB-007**: System SHALL implement data retention policies
- **FR-DB-008**: System SHALL support data export for analysis

**Recommended Technology**: PostgreSQL with TimescaleDB extension

#### 3.9.2 Caching

**Priority**: P1 (High)  
**Status**: ❌ Not Implemented

**Functional Requirements**:

- **FR-CACHE-001**: System SHALL cache market data for quick retrieval
- **FR-CACHE-002**: System SHALL cache computed indicators
- **FR-CACHE-003**: System SHALL implement cache invalidation strategy
- **FR-CACHE-004**: System SHALL support distributed caching (Redis)

### 3.10 API Integration System (Planned)

#### 3.10.1 Multi-API Framework

**Priority**: P2 (Medium)  
**Status**: ❌ Architecture ready, not implemented

**Functional Requirements**:

- **FR-INT-001**: System SHALL support pluggable API connector architecture
- **FR-INT-002**: Each API connector SHALL be independent and self-contained
- **FR-INT-003**: System SHALL normalize data from different API sources
- **FR-INT-004**: System SHALL handle API rate limiting
- **FR-INT-005**: System SHALL implement API failover and redundancy
- **FR-INT-006**: System SHALL log all API interactions
- **FR-INT-007**: System SHALL support 100+ concurrent API connections

**Target Integrations**:
- TradingView
- Polygon.io
- OANDA
- Binance
- MetaTrader 5
- News APIs (NewsAPI, Bloomberg, Reuters)
- Social sentiment (Twitter, Reddit, StockTwits)
- Volatility feeds (VIX, VVIX)

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Web Dashboard

**Description**: Browser-based trading dashboard

**Requirements**:
- **UI-001**: SHALL support modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **UI-002**: SHALL be responsive (1280x720 minimum, 1920x1080 recommended)
- **UI-003**: SHALL provide dark mode UI (current default)
- **UI-004**: SHALL use TailwindCSS for consistent styling
- **UI-005**: SHALL achieve 60 FPS during real-time updates
- **UI-006**: SHALL be accessible (WCAG 2.1 Level AA) (future)

### 4.2 Hardware Interfaces

**Requirements**:
- **HW-001**: System SHALL run on x86_64 or ARM64 architecture
- **HW-002**: Minimum 4GB RAM (8GB recommended)
- **HW-003**: Minimum 10GB disk space (100GB+ recommended for data storage)
- **HW-004**: Network interface with stable internet connection

### 4.3 Software Interfaces

#### 4.3.1 Interactive Brokers API

**Interface Type**: TCP Socket  
**Protocol**: IB API (ibapi)  
**Port**: 7497 (paper trading), 7496 (live trading)

**Requirements**:
- **SI-IB-001**: SHALL connect to IBKR TWS or IB Gateway
- **SI-IB-002**: SHALL authenticate with valid IBKR credentials
- **SI-IB-003**: SHALL subscribe to market data for authorized symbols
- **SI-IB-004**: SHALL handle API rate limits (max 50 messages/second)
- **SI-IB-005**: SHALL implement reconnection logic

#### 4.3.2 Database Interface (Future)

**Interface Type**: PostgreSQL  
**Protocol**: TCP/PostgreSQL wire protocol  
**Port**: 5432

**Requirements**:
- **SI-DB-001**: SHALL support PostgreSQL 14+
- **SI-DB-002**: SHALL use TimescaleDB extension for time-series data
- **SI-DB-003**: SHALL use connection pooling
- **SI-DB-004**: SHALL implement prepared statements for security

#### 4.3.3 Message Queue Interface (Future)

**Interface Type**: Redis or Kafka  
**Protocol**: Redis RESP or Kafka protocol

**Requirements**:
- **SI-MQ-001**: SHALL support Redis 7+ or Kafka 3.0+
- **SI-MQ-002**: SHALL implement publish/subscribe pattern
- **SI-MQ-003**: SHALL persist messages for at least 24 hours
- **SI-MQ-004**: SHALL support message replay

### 4.4 Communication Interfaces

#### 4.4.1 WebSocket Interface

**Protocol**: RFC 6455 (WebSocket)  
**Port**: 8080  
**Endpoint**: `ws://localhost:8080/ws`

**Message Format**: JSON

**Requirements**:
- **CI-WS-001**: SHALL use JSON for message serialization
- **CI-WS-002**: SHALL implement message validation
- **CI-WS-003**: SHALL support compression (permessage-deflate)
- **CI-WS-004**: SHALL implement heartbeat every 30 seconds
- **CI-WS-005**: SHALL timeout idle connections after 5 minutes

#### 4.4.2 REST API Interface (Future)

**Protocol**: HTTP/1.1 or HTTP/2  
**Port**: 8080  
**Base Path**: `/api/v1`

**Requirements**:
- **CI-REST-001**: SHALL use JSON for request/response bodies
- **CI-REST-002**: SHALL implement RESTful principles
- **CI-REST-003**: SHALL use standard HTTP status codes
- **CI-REST-004**: SHALL support CORS for browser clients
- **CI-REST-005**: SHALL implement JWT authentication (future)

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

- **NFR-PERF-001**: Tick processing latency SHALL be < 10ms (p99)
- **NFR-PERF-002**: Strategy execution latency SHALL be < 50ms (p99)
- **NFR-PERF-003**: WebSocket message propagation SHALL be < 100ms (p99)
- **NFR-PERF-004**: Dashboard UI SHALL update within 100ms of signal generation
- **NFR-PERF-005**: System SHALL handle 100 ticks/second per symbol
- **NFR-PERF-006**: System SHALL support 10 concurrent symbol subscriptions
- **NFR-PERF-007**: Frontend SHALL maintain 60 FPS during updates
- **NFR-PERF-008**: System SHALL use < 2GB RAM in normal operation
- **NFR-PERF-009**: System SHALL use < 10% CPU in idle state

### 5.2 Safety Requirements

- **NFR-SAFE-001**: System SHALL prevent double order submission
- **NFR-SAFE-002**: System SHALL implement kill switch for emergency position closure
- **NFR-SAFE-003**: System SHALL enforce maximum position size limits
- **NFR-SAFE-004**: System SHALL enforce maximum daily loss limits
- **NFR-SAFE-005**: System SHALL validate all orders before submission
- **NFR-SAFE-006**: System SHALL implement circuit breakers for abnormal market conditions
- **NFR-SAFE-007**: System SHALL log all critical operations for audit trail

### 5.3 Security Requirements

- **NFR-SEC-001**: System SHALL NOT store broker credentials in plain text
- **NFR-SEC-002**: System SHALL use environment variables for sensitive configuration
- **NFR-SEC-003**: System SHALL implement authentication for API access (future)
- **NFR-SEC-004**: System SHALL use HTTPS/WSS in production (future)
- **NFR-SEC-005**: System SHALL implement role-based access control (future)
- **NFR-SEC-006**: System SHALL encrypt data at rest (future)
- **NFR-SEC-007**: System SHALL implement audit logging
- **NFR-SEC-008**: System SHALL validate and sanitize all user inputs

### 5.4 Reliability Requirements

- **NFR-REL-001**: System SHALL achieve 99.9% uptime during market hours
- **NFR-REL-002**: System SHALL recover from crashes within 30 seconds
- **NFR-REL-003**: System SHALL reconnect to IBKR within 5 seconds of disconnection
- **NFR-REL-004**: System SHALL maintain state across restarts (future with database)
- **NFR-REL-005**: System SHALL implement health checks for all components
- **NFR-REL-006**: System SHALL gracefully handle component failures

### 5.5 Availability Requirements

- **NFR-AVAIL-001**: System SHALL be available during forex market hours (24/5)
- **NFR-AVAIL-002**: System SHALL support planned maintenance windows
- **NFR-AVAIL-003**: System SHALL notify users of downtime events
- **NFR-AVAIL-004**: System SHALL implement failover for critical components (future)

### 5.6 Maintainability Requirements

- **NFR-MAINT-001**: Code SHALL follow PEP 8 (Python) and ESLint (TypeScript) standards
- **NFR-MAINT-002**: All functions SHALL have docstrings/comments
- **NFR-MAINT-003**: System SHALL have modular architecture for easy component replacement
- **NFR-MAINT-004**: System SHALL use dependency injection where applicable
- **NFR-MAINT-005**: System SHALL maintain comprehensive documentation
- **NFR-MAINT-006**: System SHALL have unit test coverage > 70% (future)

### 5.7 Portability Requirements

- **NFR-PORT-001**: System SHALL run on macOS, Linux, and Windows (WSL2)
- **NFR-PORT-002**: System SHALL be containerized with Docker
- **NFR-PORT-003**: System SHALL use platform-agnostic dependencies
- **NFR-PORT-004**: System SHALL support deployment to cloud platforms (AWS, GCP, Azure)

### 5.8 Scalability Requirements

- **NFR-SCALE-001**: System SHALL support horizontal scaling (future with Kubernetes)
- **NFR-SCALE-002**: System SHALL support 100+ concurrent API integrations
- **NFR-SCALE-003**: System SHALL support 20+ concurrent trading strategies
- **NFR-SCALE-004**: System SHALL support 1000+ messages/second (future with Kafka)
- **NFR-SCALE-005**: Database SHALL support 100M+ historical records (future)

### 5.9 Monitoring and Observability Requirements

- **NFR-MON-001**: System SHALL implement structured logging
- **NFR-MON-002**: System SHALL expose metrics in Prometheus format (future)
- **NFR-MON-003**: System SHALL track key performance indicators (KPIs)
- **NFR-MON-004**: System SHALL implement distributed tracing (future)
- **NFR-MON-005**: System SHALL alert on critical errors
- **NFR-MON-006**: System SHALL provide health check endpoints

### 5.10 Usability Requirements

- **NFR-USE-001**: User SHALL be able to start the system with < 5 commands
- **NFR-USE-002**: Dashboard SHALL be intuitive for experienced traders
- **NFR-USE-003**: System SHALL provide clear error messages
- **NFR-USE-004**: System SHALL provide comprehensive documentation
- **NFR-USE-005**: System SHALL provide example configurations

---

## 6. Appendices

### 6.1 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend Framework | React | 18+ | UI rendering |
| Frontend Build | Vite | Latest | Development server, bundling |
| Frontend Styling | TailwindCSS | Latest | UI styling |
| Frontend Language | TypeScript | 5.0+ | Type-safe frontend code |
| Charting Library | lightweight-charts | Latest | Price charts |
| Backend Gateway | Node.js | 18+ | I/O hub |
| Gateway Framework | Express | Latest | REST API |
| WebSocket | ws | Latest | Real-time communication |
| AI/ML Runtime | Python | 3.10+ | Strategy engine |
| Numerical Computing | NumPy, Pandas | Latest | Data processing |
| ML Framework | PyTorch | Latest | Deep learning |
| Broker API | ibapi | Latest | IBKR integration |
| Database (Planned) | PostgreSQL | 14+ | Data persistence |
| Time-Series DB | TimescaleDB | Latest | Time-series optimization |
| Message Queue (Planned) | Redis / Kafka | Latest | Message reliability |
| Monitoring (Planned) | Prometheus, Grafana | Latest | Observability |
| Container Platform | Docker | Latest | Containerization |
| Orchestration (Planned) | Kubernetes | Latest | Production deployment |

### 6.2 Glossary

See Section 1.5 for definitions and abbreviations.

### 6.3 Analysis Models

#### 6.3.1 Data Flow Diagram

```
[IBKR TWS] → [Tick Stream] → [Candle Engine] → [Strategy Manager] → [Signal Router] → [WebSocket] → [Node Gateway] → [Frontend]
```

#### 6.3.2 Component Interaction

```
Frontend ←WebSocket→ Node Gateway ←WebSocket→ Python Backend
                                   ↕gRPC (future)
                                   Python AI Core
```

### 6.4 Requirements Traceability Matrix

| Requirement ID | Priority | Status | Implementation | Test Coverage |
|----------------|----------|--------|----------------|---------------|
| FR-MD-001 | P0 | ✅ | `tick_stream.py` | Integration test |
| FR-MD-009 | P0 | ✅ | `candle_engine.py` | Integration test |
| FR-STR-001 | P0 | ✅ | `strategy_manager.py` | Integration test |
| FR-SIG-001 | P0 | ✅ | `signal_router.py` | Integration test |
| FR-UI-001 | P0 | ✅ | `TradingDashboard.tsx` | Manual test |
| FR-WS-001 | P0 | ✅ | `node_gateway/index.ts` | Manual test |

*(Full matrix would include all requirements)*

### 6.5 Future Enhancements

1. **Mobile Application** (React Native)
2. **Automated Backtesting Pipeline**
3. **Strategy Marketplace** (Community-contributed strategies)
4. **Multi-Broker Support** (OANDA, Binance, MT5)
5. **Cloud Deployment Templates** (Terraform, CloudFormation)
6. **Quantum ML Experiments**
7. **On-Chain Trading Integration** (DeFi)
8. **Multi-User Support** with authentication
9. **Paper Trading Mode** (built-in simulation)
10. **Social Trading Features** (Signal sharing)

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-02 | Rizwan Beg | Initial SRS creation |

---

**Approval Signatures**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | Rizwan Beg | ___________ | ______ |
| Technical Lead | Rizwan Beg | ___________ | ______ |
| QA Angineer | ___________ | ___________ | ______ |

---

**END OF SOFTWARE REQUIREMENTS SPECIFICATION**
