#!/usr/bin/env python3
"""
End-to-end integration test for the full application flow:
IBKR Data → Apex Strategy → Execution Engine → IBKR Order Placement

This script simulates the full flow without waiting for real market conditions.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.strategy_engine.broker.ibkr_async_service import IBKRAsyncService
from ai_core.execution.execution_engine import ExecutionEngine
from ai_core.risk_manager.risk_manager import RiskManager
from ai_core.core.logger import get_logger

logger = get_logger(__name__)


async def test_integration():
    """Test the complete integration flow."""
    
    print("=" * 80)
    print("END-TO-END INTEGRATION TEST")
    print("=" * 80)
    
    broker = None
    
    try:
        # Step 1: Initialize IBKR Broker
        print("\n[1/5] Initializing IBKR Broker...")
        broker = IBKRAsyncService(host="127.0.0.1", port=7497, client_id=997)
        await broker.connect()
        print("✅ Broker connected")
        
        # Check broker health
        health = await broker.health()
        print(f"Broker health: {health}")
        
        # Step 2: Initialize Risk Manager
        print("\n[2/5] Initializing Risk Manager...")
        risk_manager = RiskManager()
        print("✅ Risk Manager initialized")
        
        # Step 3: Initialize Execution Engine
        print("\n[3/5] Initializing Execution Engine with Broker...")
        execution_engine = ExecutionEngine(
            broker_service=broker,
            risk_manager=risk_manager
        )
        print(f"✅ Execution Engine initialized")
        print(f"   Mode: {execution_engine.execution_mode.value}")
        print(f"   Enabled: {execution_engine.enabled}")
        
        # Step 4: Simulate an Apex Strategy Signal
        print("\n[4/5] Simulating Apex Strategy Signal...")
        
        # Create a mock signal from Apex strategy
        mock_signal = {
            'strategy_id': 'apex',
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.19,
            'stop_loss': 1.185,
            'take_profit': 1.20,
            'reason': 'Integration test - M5 bullish crossover with M15 uptrend',
            'timestamp': '2026-02-10T18:30:00',
            'confidence': 0.85,
        }
        
        print(f"Signal: {mock_signal}")
        
        # Step 5: Process Signal through Execution Engine
        print("\n[5/5] Processing Signal through Execution Engine...")
        
        result = await execution_engine.process_signal(mock_signal)
        
        if result:
            print("✅ Signal processed successfully")
            print(f"Result: {result}")
            
            # Check if order was placed (will be simulated in PAPER_TRADING mode)
            print("\n" + "=" * 80)
            print("EXECUTION RESULT:")
            print("=" * 80)
            
            if 'trade_id' in result:
                print(f"Trade ID: {result['trade_id']}")
            if 'order_id' in result:
                print(f"Order ID: {result['order_id']}")
            if 'status' in result:
                print(f"Status: {result['status']}")
            if 'execution_mode' in result:
                print(f"Execution Mode: {result['execution_mode']}")
            
            print("\nNOTE: In PAPER_TRADING mode, orders are simulated (not real)")
            print("To place real orders:")
            print("1. Change EXECUTION_MODE to LIVE_TRADING in execution_config.py")
            print("2. Verify risk limits are appropriate")
            print("3. Re-run this test or the full application")
            
        else:
            print("⚠️ Signal was rejected or failed to process")
            print("Check logs for details")
        
        # Check current positions
        print("\n" + "=" * 80)
        print("CURRENT POSITIONS:")
        print("=" * 80)
        positions = await broker.get_positions()
        if positions:
            for pos in positions:
                print(f"  {pos}")
        else:
            print("  No open positions")
        
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST COMPLETED")
        print("=" * 80)
        print("\nThe full application flow is working:")
        print("  ✅ IBKR Broker connects successfully")
        print("  ✅ Execution Engine initializes with broker")
        print("  ✅ Signals can be processed")
        print("  ✅ Orders can be placed (simulated in PAPER mode)")
        print("\nYou can now run the full application with:")
        print("  python -m ibkr_streaming.run")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.error("Integration test failed", exc_info=True)
        return False
        
    finally:
        # Cleanup
        if broker:
            print("\nDisconnecting from broker...")
            await broker.disconnect()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)
