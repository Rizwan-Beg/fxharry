/**
 * Node Gateway Main Entry Point
 * Express server with WebSocket support, gRPC client, and REST API routes
 */

import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createAIClient } from './grpc_clients/ai_client';
import apiRoutes from './api/routes';
import { errorMiddleware } from './api/middlewares';
import { ClientManager } from './websockets/client.manager';

const app = express();
app.use(cors());
app.use(express.json());

const port = process.env.PORT ? Number(process.env.PORT) : 8080;
const grpcHost = process.env.GRPC_HOST || 'localhost';
const grpcPort = process.env.GRPC_PORT ? Number(process.env.GRPC_PORT) : 50051;

// Health route
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', grpc: `${grpcHost}:${grpcPort}`, timestamp: new Date().toISOString() });
});

// API routes
app.use('/api', apiRoutes);

// Error handling middleware (must be last)
app.use(errorMiddleware);

const server = app.listen(port, () => {
  console.log(`Node Gateway listening on http://0.0.0.0:${port}`);
  console.log(`gRPC connection: ${grpcHost}:${grpcPort}`);
});

// WebSocket server for real-time updates
const wss = new WebSocketServer({ server, path: '/ws' });
const clientManager = new ClientManager(wss);

wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'welcome', ts: Date.now() }));
});

// Connect to Python gRPC and stream market data to clients
const client = createAIClient(`${grpcHost}:${grpcPort}`);

function broadcast(obj: any) {
  const msg = JSON.stringify(obj);
  clientManager.broadcast(msg);
}

// Start streaming for default symbols
const stream = client.StreamMarketData({ symbols: ['EURUSD', 'GBPUSD', 'XAUUSD'] });
stream.on('data', (update: any) => {
  broadcast({ type: 'market_data', data: update });
});
stream.on('error', (err: any) => {
  console.error('gRPC stream error:', err);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});