/**
 * Node Gateway Main Entry Point
 * Express server with WebSocket support, gRPC client, and REST API routes
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import { WebSocketServer, WebSocket } from 'ws';
import apiRoutes from './api/routes/index.js';
import { errorMiddleware } from './api/middlewares/index.js';
import { ClientManager } from './websockets/client.manager.js';
import { broadcastMarketData, setClientManager } from './websockets/market.stream.js';

const app = express();
app.use(cors());
app.use(express.json());

const port = process.env.PORT ? Number(process.env.PORT) : 8080;
const grpcHost = process.env.GRPC_HOST || 'localhost';
const grpcPort = process.env.GRPC_PORT ? Number(process.env.GRPC_PORT) : 50051;

// Health route
app.get('/api/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', grpc: `${grpcHost}:${grpcPort}`, timestamp: new Date().toISOString() });
});

// API routes
app.use('/api', apiRoutes);

// Error handling middleware (must be last)
app.use(errorMiddleware);

const server = app.listen(port, () => {
  console.log(`Node Gateway listening on http://0.0.0.0:${port}`);
});

// WebSocket server for real-time updates
const wss = new WebSocketServer({ server, path: '/ws' });
const clientManager = new ClientManager(wss);
setClientManager(clientManager);

wss.on('connection', (ws: WebSocket) => {
  ws.send(JSON.stringify({ type: 'welcome', ts: Date.now() }));
  ws.on('message', (msg: Buffer) => {
    try {
      const data = JSON.parse(msg.toString());
      broadcastMarketData(data);
    } catch {}
  });
});

// gRPC streaming disabled to avoid conflicts with Python streamer

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});