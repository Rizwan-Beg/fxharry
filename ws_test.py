import asyncio
import websockets
import json

async def test_ws():
    try:
        async with websockets.connect('ws://localhost:3001') as websocket:
            print("Connected to WS")
            for _ in range(10):
                msg = await websocket.recv()
                data = json.loads(msg)
                print(f"Received: {data['type']}")
                if data['type'] == 'strategy_diagnostics':
                    print(f"Diagnostics: {data}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_ws())
