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
  console.log(`✅ Node Gateway listening on http://0.0.0.0:${port}`);
  console.log(`✅ WebSocket server ready at ws://localhost:${port}/ws`);
});

// WebSocket server for real-time updates
const wss = new WebSocketServer({ server, path: '/ws' });
const clientManager = new ClientManager(wss);
setClientManager(clientManager);

// Log when WebSocket server is ready
wss.on('listening', () => {
  console.log(`✅ WebSocket server listening on ws://localhost:${port}/ws`);
});

// Track Python backend connection separately
let pythonConnection: WebSocket | null = null;

// Handle WebSocket connections (both Python backend and React frontend)
wss.on('connection', (ws: WebSocket, req) => {
  // Detect if this is Python backend (sends tick messages) or React frontend
  let isPythonBackend = false;
  let messageCount = 0;
  let loggedConnection = false; // Track if we've logged this connection
  
  // Send welcome message
  try {
    ws.send(JSON.stringify({ type: 'welcome', ts: Date.now() }));
  } catch (err) {
    // Connection might be closed already
  }
  
  // Don't add to client manager yet - wait to see if it's Python or frontend
  // We'll add frontend connections after first non-tick message
  
  // Handle incoming messages
  ws.on('message', (msg: Buffer) => {
    try {
      const data = JSON.parse(msg.toString());
      messageCount++;
      
      // If message has type 'tick', it's from Python backend
      if (data.type === 'tick' || data.type === 'market_data') {
        if (!isPythonBackend) {
          // First tick message from this connection - mark as Python backend
          isPythonBackend = true;
          
          // Close old Python connection if exists and is different
          if (pythonConnection && pythonConnection !== ws && pythonConnection.readyState === WebSocket.OPEN) {
            try {
              pythonConnection.close();
            } catch {}
          }
          pythonConnection = ws;
          if (!loggedConnection) {
            console.log('✅ Connected to Python IBKR Stream');
            loggedConnection = true;
          }
        }
        // Only log every 50th message to reduce spam
        if (messageCount % 50 === 0) {
          console.log(`📊 Received market data from Python: ${data.symbol || 'unknown'} (${messageCount} messages)`);
        }
        broadcastMarketData(data);
      } else {
        // Frontend message - add to client manager if not already added
        if (!isPythonBackend && !loggedConnection) {
          clientManager.addClient(ws);
          console.log(`✅ Frontend WebSocket connected (Total clients: ${clientManager.getClientCount()})`);
          loggedConnection = true;
        }
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
    }
  });
  
  ws.on('close', () => {
    if (isPythonBackend && pythonConnection === ws) {
      pythonConnection = null;
      console.log('Python IBKR Stream connection closed');
    } else {
      // Remove from client manager if it was a frontend connection
      clientManager.removeClient(ws);
    }
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
    // Remove from client manager on error
    if (!isPythonBackend) {
      clientManager.removeClient(ws);
    }
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