import asyncio
import websockets
import json

async def send_command():
    uri = "ws://localhost:8080/ws"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # Construct command
        # Node Gateway expects: {type: 'strategy_command', ...}
        # It forwards to Python as: {type: 'structure_command', ...}
        
        command = {
            "type": "strategy_command",
            "command": "ACTIVATE_STRATEGY",
            "strategy_id": "apex"
        }
        
        print(f"Sending: {command}")
        await websocket.send(json.dumps(command))
        print("Command sent!")
        
        # Listen for response (strategy_status broadcast)
        print("Waiting for response...")
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {response}")
            
            # Might be welcome message first, so wait for status
            if "welcome" in response:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {response}")
                
        except asyncio.TimeoutError:
            print("Timeout waiting for response")

if __name__ == "__main__":
    asyncio.run(send_command())
