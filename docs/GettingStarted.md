# Running the AI Forex Trading Project

This guide explains how to run the full stack: Python IBKR stream, Node Gateway, and the React frontend.

## Prerequisites
- Node.js v18+ and npm
- Python 3.10+ with `pip`
- IBKR TWS or IB Gateway running locally
  - Host `127.0.0.1`, Port `7497` for paper (or `7496` for live)
- Installed Python packages:
  - `ib_async`, `websockets`

## Configure
- IBKR client settings:
  - Edit `ibkr_streaming/config.py` if needed:
    - `IBKR_HOST`, `IBKR_PORT`, `IBKR_CLIENT_ID`
    - `NODE_GATEWAY_WS_URL` should be `ws://localhost:8080/ws`
- Frontend WebSocket URL (optional):
  - Set `VITE_WS_URL` in env to override, or defaults to `ws://localhost:8080/ws` via `frontend/src/services/ws.ts`.

## Start Node Gateway
- In a terminal:
  - `cd node_gateway`
  - `npm start`
- Expected logs:
  - `✅ Node Gateway listening on http://0.0.0.0:8080`
  - `✅ WebSocket server ready at ws://localhost:8080/ws`

## Start Frontend
- In another terminal:
  - `cd frontend`
  - `npm run dev`
- Open the app:
  - `http://localhost:5173/` (Vite may use another port if 5173 is busy)

## Start Python IBKR Streaming
- In a third terminal:
  - `python3 -m ibkr_streaming.run`
- Logs write to `logs/ibkr_streaming_YYYYMMDD.log`. You should see:
  - IBKR connection established, contract qualification, and continuous tick pushes
  - WebSocket connected to Node Gateway and `[PUSH] Sent data for <symbol>`

## Verify Connectivity
- Quick diagnostic:
  - From project root: `python3 test_connections.py`
  - Should report:
    - HTTP Health: PASS
    - WebSocket Connection: PASS

## Data Flow
- Python IBKR → Node Gateway (WebSocket) → Frontend (WebSocket)
- Node normalizes Python `tick` into `market_data` with `bid/ask/mid/spread/open/high/low/close/candle/timestamp` in `node_gateway/src/websockets/market.stream.ts`.
- Frontend listens and renders:
  - WebSocket hook: `frontend/src/hooks/useLiveFeed.ts`
  - Chart: `frontend/src/components/TradingChart.tsx` → `PriceChart.tsx`

## Troubleshooting
- Port in use `EADDRINUSE: 8080`:
  - Stop extra Node Gateway instances or change the port via env `PORT`.
- IBKR `clientId already in use`:
  - Change `IBKR_CLIENT_ID` in `ibkr_streaming/config.py` (e.g., to `103`) and restart streaming.
- Frontend not rendering:
  - Ensure Node Gateway is running and WS reachable at `ws://localhost:8080/ws`
  - Confirm Python logs show `[PUSH] Sent data` and Node receives ticks
  - Frontend chart requires container width; `PriceChart` waits for non-zero size then initializes

## Optional Commands
- Lint frontend:
  - `cd frontend && npm run lint`
- Build Node Gateway (TypeScript):
  - `cd node_gateway && npm run build`

## Notes
- The frontend WebSocket and chart are StrictMode-safe; connections persist and reconnects are graceful.
- Candles render immediately using per-second buckets; if desired, adapt the chart to line-series for mid-price visualization.