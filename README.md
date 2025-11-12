## FXHarry Institutional Trading Platform

### Overview
- AI-first trading stack mixing FastAPI backend, Vite/React frontend, and future ML/RL services.
- Supports broker integrations, strategy orchestration, WebSocket streaming, and GenAI tooling.
- Restructured for modular growth across broker connectivity, backtesting, risk, and sentiment analytics.
- Includes placeholders for ML pipelines, GenAI agents, transformers, and reinforcement learning assets.
- Docker Compose orchestrates Postgres, Redis, backend, frontend, and optional Celery workers.

### Repository Layout
- `backend/`: FastAPI application plus service, data, and AI modules.
  - `core/`: shared config, logging, and utilities.
  - `api/routes/`: account, strategies, trades, and backtesting endpoints.
  - `services/`: domain services split across broker, strategy, sentiment, execution, backtesting, and risk.
  - `ai_models/`: placeholders for RL, transformer, and agentic model assets.
  - `websocket/`: real-time connection management.
  - `Dockerfile`, `requirements.txt`, `.env.example` for container builds.
- `frontend/`: Vite + React + Tailwind dashboard scaffolding with `src/components`, `hooks`, `context`, `pages`, `utils`.
- `ml_pipeline/`: feature engineering, training, evaluation, deployment stubs, notebooks for research.
- `genai_agent/`: LLM brain, news analyzer, and decision fusion placeholders.
- `tests/`: test harness entry-point ready for API/service coverage.
- `docker-compose.yml`: multi-service stack (Postgres, Redis, FastAPI backend, Vite frontend, Celery worker).
- `setup.py`: enables backend packaging and dependency management.
- `archive/`: legacy `client` and `server` directories retained for reference (contain immutable artifacts; remove manually if desired).

### Getting Started
- `python -m venv venv && source venv/bin/activate` to create a virtual environment.
- `pip install -r backend/requirements.txt` to install backend dependencies.
- `cd frontend && npm install` to set up the React dashboard.
- Configure environment variables via `backend/.env.example` copied to `.env`.
- Launch everything with `docker-compose up --build` or run services locally:
  - `uvicorn backend.main:app --reload`
  - `cd frontend && npm run dev`

### Backend Highlights
- Structured logging powered by `backend/core/logger.get_logger`.
- Centralized settings in `backend/core/config`.
- Broker abstraction under `backend/services/broker/` with IBKR implemented plus placeholders for OANDA, MT5, Binance.
- Strategy engine split into rule-based, ML, and reinforcement agents.
- Backtesting engine rebuilt under `backend/services/backtesting/engine.py` with async support.
- Risk management, market data simulation, and sentiment analyzer scaffolds ready for production integrations.
- WebSocket streaming managed via `backend/websocket/connection_manager.py`.

### Frontend Notes
- Components under `frontend/src/components` mirror the trading dashboard widgets.
- Hooks such as `useMarketData` and `useWebSocket` connect to the backend stream.
- Placeholder directories (`context`, `pages`, `utils`) document future UI architecture.

### ML & GenAI Roadmap
- `ml_pipeline/` reserved for feature engineering, training orchestrations, evaluation suites, and deployment (BentoML/TorchServe).
- `genai_agent/` modules will orchestrate LangChain + FinBERT news ingestion, summarization, and signal fusion.
- `backend/services/sentiment_analyzer` houses FinBERT and news collectors ready for extension.
- `backend/services/strategy_engine/reinforcement_agent.py` scaffolds RL policy logic for deep trading strategies.

### Testing & Quality
- Add API and service tests under `tests/` using `pytest` or `pytest-asyncio`.
- Integrate linting/formatting (e.g., `ruff`, `black`, `mypy`) as part of CI.

### Operations Checklist
- Run `docker-compose up --build` to verify the stack (backend on `localhost:8000`, frontend on `localhost:3000`).
- Confirm Postgres (`localhost:5432`) and Redis (`localhost:6379`) connectivity.
- Tail logs via the configured async logger for real-time observability.
- On macOS, legacy artifacts under `archive/` may have immutable flags; clear manually if you prefer a clean tree.

### Next Steps
- Implement broker-specific services by extending `BaseBroker`.
- Populate ML orchestrators and RL agents with actual model code.
- Wire sentiment analyzer to real data sources and integrate with decision layer.
- Expand frontend pages for strategy management, execution control, and analytics dashboards.
