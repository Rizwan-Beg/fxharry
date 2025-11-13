/**
 * WebSocket Client Manager
 * Manages WebSocket connections and broadcasting
 */

import { WebSocketServer, WebSocket } from 'ws';

export class ClientManager {
  private clients: Set<WebSocket> = new Set();
  private wss: WebSocketServer;

  constructor(wss: WebSocketServer) {
    this.wss = wss;
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      this.addClient(ws);
    });
  }

  addClient(ws: WebSocket): void {
    this.clients.add(ws);
    
    ws.on('close', () => {
      this.removeClient(ws);
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      this.removeClient(ws);
    });
  }

  removeClient(ws: WebSocket): void {
    this.clients.delete(ws);
  }

  broadcast(message: string): void {
    const deadClients: WebSocket[] = [];
    
    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(message);
        } catch (error) {
          console.error('Error broadcasting to client:', error);
          deadClients.push(client);
        }
      } else {
        deadClients.push(client);
      }
    }

    // Clean up dead clients
    deadClients.forEach(client => this.removeClient(client));
  }

  getClientCount(): number {
    return this.clients.size;
  }
}