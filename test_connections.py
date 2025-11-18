#!/usr/bin/env python3
"""
Test script to verify WebSocket connections
"""
import asyncio
import websockets
import json
import sys

NODE_GATEWAY_WS_URL = "ws://localhost:8080/ws"

async def test_python_to_node():
    """Test Python → Node Gateway connection"""
    print("=" * 60)
    print("Testing Python → Node Gateway WebSocket Connection")
    print("=" * 60)
    
    try:
        print(f"Attempting to connect to {NODE_GATEWAY_WS_URL}...")
        async with websockets.connect(
            NODE_GATEWAY_WS_URL,
            ping_interval=20,
            ping_timeout=10
        ) as ws:
            print("✅ Successfully connected to Node Gateway!")
            
            # Wait for welcome message
            try:
                welcome = await asyncio.wait_for(ws.recv(), timeout=2.0)
                welcome_data = json.loads(welcome)
                if welcome_data.get('type') == 'welcome':
                    print(f"✅ Received welcome message: {welcome_data}")
                else:
                    print(f"⚠️  Received unexpected message: {welcome_data}")
            except asyncio.TimeoutError:
                print("⚠️  No welcome message received (might be OK)")
            
            # Send a test tick message
            test_message = {
                "type": "tick",
                "symbol": "EURUSD",
                "tick": {
                    "bid": 1.16110,
                    "ask": 1.16115,
                    "mid": 1.161125,
                    "spread": 0.00005,
                    "timestamp": 1234567890
                },
                "candle": {},
                "micro": {}
            }
            
            print(f"\n📤 Sending test message: {test_message['symbol']}")
            await ws.send(json.dumps(test_message))
            print("✅ Message sent successfully!")
            
            # Wait a bit to see if we get any response
            await asyncio.sleep(1)
            
            print("\n✅ Connection test PASSED!")
            return True
            
    except ConnectionRefusedError:
        print(f"❌ Connection refused! Node Gateway is not running on port 8080")
        print("   Start Node Gateway: cd node_gateway && npm start")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def test_http_health():
    """Test HTTP health endpoint"""
    import urllib.request
    print("\n" + "=" * 60)
    print("Testing Node Gateway HTTP Health Endpoint")
    print("=" * 60)
    
    try:
        url = "http://localhost:8080/api/health"
        print(f"Checking {url}...")
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Health check passed: {data}")
            return True
    except urllib.error.URLError as e:
        print(f"❌ Health check failed: {e}")
        print("   Node Gateway HTTP server is not running")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def main():
    """Run all connection tests"""
    print("\n🔍 Connection Diagnostic Tool")
    print("=" * 60)
    
    # Test HTTP first (easier check)
    http_ok = await test_http_health()
    
    if not http_ok:
        print("\n⚠️  Node Gateway is not running!")
        print("   Please start it first: cd node_gateway && npm start")
        sys.exit(1)
    
    # Test WebSocket
    ws_ok = await test_python_to_node()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"HTTP Health Check: {'✅ PASS' if http_ok else '❌ FAIL'}")
    print(f"WebSocket Connection: {'✅ PASS' if ws_ok else '❌ FAIL'}")
    
    if http_ok and ws_ok:
        print("\n✅ All connections working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some connections failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

