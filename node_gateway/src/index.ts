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

// Track Python backend connection separately
let pythonConnection: WebSocket | null = null;

// Handle WebSocket connections (both Python backend and React frontend)
wss.on('connection', (ws: WebSocket, req) => {
  // Detect if this is Python backend (sends tick messages) or React frontend
  let isPythonBackend = false;
  
  // Send welcome message
  ws.send(JSON.stringify({ type: 'welcome', ts: Date.now() }));
  
  // Add to client manager initially (for frontend connections)
  // We'll remove it if it turns out to be Python backend
  clientManager.addClient(ws);
  
  // Handle incoming messages
  ws.on('message', (msg: Buffer) => {
    try {
      const data = JSON.parse(msg.toString());
      
      // If message has type 'tick', it's from Python backend
      if (data.type === 'tick' || data.type === 'market_data') {
        if (!isPythonBackend) {
          // First tick message from this connection - mark as Python backend
          isPythonBackend = true;
          // Remove from client manager (Python doesn't need to receive broadcasts)
          clientManager.removeClient(ws);
          
          // Close old Python connection if exists
          if (pythonConnection && pythonConnection !== ws) {
            try {
              pythonConnection.close();
            } catch {}
          }
          pythonConnection = ws;
          console.log('✅ Connected to Python IBKR Stream');
        }
        console.log(`📊 Received market data from Python: ${data.symbol || 'unknown'}`);
        broadcastMarketData(data);
      }
      // Frontend messages don't need special handling - they're already in client manager
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
    }
  });
  
  ws.on('close', () => {
    if (isPythonBackend && pythonConnection === ws) {
      pythonConnection = null;
      console.log('Python IBKR Stream connection closed');
    } else {
      console.log('Frontend WebSocket connection closed');
    }
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
  
  // Log connection (we'll know if it's Python after first message)
  console.log(`✅ WebSocket connected (Total clients: ${clientManager.getClientCount()})`);
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