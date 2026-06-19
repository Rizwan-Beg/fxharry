const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:3001');

ws.on('open', function open() {
  console.log('Connected to WS');
});

ws.on('message', function incoming(data) {
  const msg = JSON.parse(data);
  console.log('Received type:', msg.type);
  if (msg.type === 'strategy_diagnostics') {
      console.log('Diagnostics:', msg.data);
  }
});

setTimeout(() => {
    ws.close();
    process.exit(0);
}, 5000);
