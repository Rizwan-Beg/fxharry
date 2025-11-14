// node_gateway/src/integrations/ibkr/ibkr.bridge.ts

import WebSocket from "ws";
import { broadcastMarketData } from "../../websockets/market.stream";

export function startIBKRBridge() {
    const url = process.env.PYTHON_WS_URL;
    if (!url) {
        console.log("IBKR bridge disabled; Python pushes directly to Node WS");
        return;
    }
    const pythonWS = new WebSocket(url);
    pythonWS.on("open", () => {
        console.log("Connected to Python IBKR Stream");
    });
    pythonWS.on("message", (msg) => {
        try {
            const data = JSON.parse(msg.toString());
            broadcastMarketData(data);
        } catch {}
    });
    pythonWS.on("close", () => {
        console.log("Python IBKR Stream closed");
    });
    pythonWS.on("error", (err) => {
        console.log("Python WS Error:", err);
    });
}
