🚀 QuantX — AI-Powered Multi-Agent Forex Trading System
Advanced Hybrid Architecture for ML, RL, GenAI & 100+ API Integrations
QuantX is a next-generation, full-stack quantitative trading platform designed for:
Individual quant traders
Advanced AI researchers
Algo trading enthusiasts
Developers building institutional-grade trading systems

The architecture supports:
Real-time forex market execution
100+ external APIs (brokers, news, LLMs, data sources)
AI-powered signals with ML, DL, RL
GenAI-driven strategy reasoning
C++-accelerated optional execution engine
Modular strategies
Professional trading dashboard
This system mirrors the architecture used in Two Sigma, Citadel, Jane Street, and modern AI agent frameworks — but optimized so a single person can maintain and extend it.

🧠 Why This Project Exists
Trading today is not about writing simple indicators.
It is about building intelligent multi-agent systems that combine:
Statistical modeling
Deep learning
Reinforcement learning
Market microstructure analysis
News & sentiment AI
Real-time execution
Multi-source data aggregation
QuantX is built exactly for this.

🏗️ High-Level Architecture Overview
React Dashboard (frontend/)
        ↑ WebSocket
Node.js Gateway (node_gateway/)
        ↕ gRPC + Event Streams
Python AI Core (ai_core/)
        ↕
Broker APIs / Trading Platforms / Data Sources (100+ APIs)
        ↕
Optional C++ Engine (cpp_engine/) for Low-Latency Execution

🌟 Current Live Pipeline (v1.0)
The system is currently running a fully integrated live-execution pipeline:
- **Strategy Engine**: Running the `Apex` Multi-Timeframe (MTF) strategy. It aligns M15 directional bias with M5 momentum crossovers during active London/NY sessions.
- **LLM Gatekeeper**: Signals are routed to an AI Agent powered by `llama-3.1-8b` (via Groq). The LLM actively pulls live News sentiment and macroeconomic data to vet technical signals before execution.
- **Trade Scorer**: Mathematical validation of signals against market regime (ADX/ATR) to ensure execution only in favorable conditions.
- **Execution Engine**: Direct integration with Interactive Brokers (IBKR TWS) via `ib_async`. Features automated bracket order generation (Take Profit & Stop Loss), CFD routing, strict 5-decimal tick compliance, and in-memory position tracking.
- **Frontend Dashboard**: A comprehensive React UI featuring real-time AI reasoning logs, an interactive Trade History modal, and live account equity tracking.

🔥 Key Features
🧬 Multi-Agent AI Strategy System
Rule-based strategies
Hybrid ML/AI strategies
Reinforcement Learning agents
GenAI reasoning agents (LLM Agent using MCP)
Sentiment + news strategies
Strategy auto-selection based on market conditions

📡 Multi-API Integration Engine
Node.js handles 100+ data sources simultaneously:
TradingView
Polygon.io
IBKR
OANDA
Binance
MT5
News APIs
Social sentiment feeds
LLM inference APIs
Volatility feeds
Liquidity providers

⚙️ Real-Time Execution
WebSocket streaming
Ultra-fast order execution
Multi-broker routing
Risk management
Live position monitoring
Low latency path (optionally via C++)

📊 Professional React Dashboard
Real-time charts
AI strategy cards with confidence %
Signals feed
Quick trade panel
Portfolio + risk metrics
Live session info

🧱 Folder Structure (Final Architecture)
fxharry-main/
│
├── frontend/            # React dashboard (UI)
│   ├── src/
│   └── public/
│
├── node_gateway/        # Node.js execution & API engine
│   ├── api/
│   ├── brokers/
│   ├── integrations/    # 100+ API modules
│   ├── websockets/
│   └── grpc_clients/
│
├── ai_core/             # Python AI/ML/GenAI/RL engine
│   ├── ml_engine/
│   ├── strategy_engine/
│   ├── genai/
│   ├── backtesting/
│   ├── risk_manager/
│   └── grpc_server.py
│
├── cpp_engine/          # High-frequency execution modules
│
├── shared/              # Cross-language schemas & proto files
│
├── infra/               # Docker, deployment, configs
│
├── tests/               # Testing suite
│
└── docker-compose.yml   # Multi-service orchestration

🔌 Why a Hybrid Architecture (Node + Python + React + C++)?
✔ React
Best UI for real-time dashboards.

✔ Node.js
Handles massive I/O, ideal for 100+ APIs, websockets, brokers.

✔ Python
Industry standard for ML/DL/RL/GenAI and quant research.

✔ C++ (optional)
Provides HFT-level performance when needed.

This combination gives you a future-proof quant stack.

🔄 Data Flow (End-to-End)
                     ┌──────────────────────────┐
                     │   100+ External APIs     │
                     │  Brokers | Data | News   │
                     └──────────────────────────┘
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │     Node Gateway         │
                     │  - Integrations          │
                     │  - Data Normalization    │
                     │  - WebSockets            │
                     └──────────────────────────┘
                                  │ gRPC
                                  ▼
                     ┌──────────────────────────┐
                     │       Python AI Core     │
                     │ - ML/DL Models           │
                     │ - RL Agents              │
                     │ - GenAI LLM Agents       │
                     │ - Strategy Engine        │
                     └──────────────────────────┘
                                  │ Signals
                                  ▼
                     ┌──────────────────────────┐
                     │      Node Gateway        │
                     │  Order Routing           │
                     └──────────────────────────┘
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │     Trading DashBoard    │
                     └──────────────────────────┘

🧬 Strategy Engine Design

Strategies live in:

ai_core/strategy_engine/

Types of Strategies:
Type	Description
Rule-Based	SMA, RSI, MACD, structure-based
ML-Based	LSTM/Transformer prediction models
RL-Based	PPO, SAC, DQN trained agents
Hybrid	AI + statistical + GenAI reasoning
Sentiment/NLP	News, FinBERT, GPT-based classification
GenAI Agent	LLM-driven strategy planning

Each strategy outputs:

{
  strategy_id: "AI-3",
  confidence: 0.63,
  direction: "SELL",
  symbol: "EURUSD",
  timestamp: ...
}


These power your Strategy Cards in the dashboard.

📡 100+ API Plugin System

All integrations live in:
node_gateway/src/integrations/


Each API:
Has its own folder
Has its own connector
Has its own normalizer
Publishes standardized events

Adding a new API =
Just add a new folder — no code rewrite required.

🧩 Why This Architecture Is Future-Proof

Supports future upgrades:
New AI models
New data APIs
New brokers
Quantum ML modules
Multi-agent LLM frameworks (MCP/LangGraph)
On-chain trading
Mobile dashboards
Automated retraining pipeline
Cluster scaling

You never need to rewrite the system again — just extend it.

🔥 Why This Is Ideal for a Solo Quant

This system lets one person achieve what usually requires:
Backend team
AI team
Frontend team
DevOps team
Data engineering team
Quant R&D team

Because the system is:
Modular
Clean
Scalable
Low maintenance
Plug-in friendly
AI driven

This is a true institutional-grade quant architecture, designed for solo execution.

🛠️ Tech Stack
Frontend
React
TypeScript
TailwindCSS
WebSockets
Node Gateway
Node.js
Express/Nest
WebSocket streams
gRPC clients
Redis/Kafka-ready
API integration engine
Python AI Core
FastAPI
gRPC
PyTorch
scikit-learn
Reinforcement learning (Stable-Baselines3 / RLlib)
LangChain / MCP
Pandas / NumPy
C++ Engine (Optional)
Order routing
Latency-critical logic

🚀 Deployment
Using Docker Compose:
docker-compose up --build

Future upgrades:
Kubernetes
Horizontal scaling
GPU model serving via Docker

🏁 Conclusion
QuantX is a professional-grade, future-ready, AI-first trading architecture designed for:
High scalability
Ultra-low latency
Powerful AI workflows
Massive API integration
Full autonomy
And a solo quant trader who wants institutional performance

This README explains everything you need to maintain, extend, and scale this system into the future.