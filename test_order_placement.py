#!/usr/bin/env python3
"""
Test script to place a simple EUR/USD BUY order to verify IBKR execution engine is working
"""
import asyncio
import time
from ai_core.strategy_engine.broker.ibkr_service import IBKRService
from ai_core.core.logger import get_logger

logger = get_logger(__name__)

async def test_order_placement():
    """Test placing a simple EUR/USD order"""
    
    # Configuration
    SYMBOL = "EURUSD"
    ACTION = "BUY"  # LONG position
    QUANTITY = 1000  # 1k units
    
    logger.info("=" * 60)
    logger.info("Testing IBKR Order Placement")
    logger.info("=" * 60)
    logger.info(f"Symbol: {SYMBOL}")
    logger.info(f"Action: {ACTION}")
    logger.info(f"Quantity: {QUANTITY}")
    logger.info("=" * 60)
    
    # Initialize IBKR Service
    # Port 7497 = Paper Trading TWS
    # Port 7496 = Live TWS
    ibkr = IBKRService(host="127.0.0.1", port=7497, client_id=999)
    
    try:
        # Connect to IBKR
        logger.info("Connecting to IBKR TWS/Gateway...")
        await ibkr.connect()
        
        if not ibkr.is_connected():
            logger.error("Failed to connect to IBKR!")
            logger.error("Make sure TWS or IB Gateway is running on port 7497")
            logger.error("And that API connections are enabled in TWS settings")
            return
        
        logger.info("✅ Successfully connected to IBKR")
        
        # Wait a bit for connection to stabilize
        await asyncio.sleep(2)
        
        # Check for next valid order ID
        if ibkr.wrapper.next_valid_id is None:
            logger.warning("Next valid order ID not received yet, waiting...")
            await asyncio.sleep(3)
        
        logger.info(f"Next valid order ID: {ibkr.wrapper.next_valid_id}")
        
        # Place the order
        logger.info(f"\n🚀 Placing {ACTION} order for {QUANTITY} {SYMBOL}...")
        result = await ibkr.place_order(
            symbol=SYMBOL,
            action=ACTION,
            quantity=QUANTITY,
            order_type="MKT"
        )
        
        if result:
            order_id = result.get('order_id')
            logger.info(f"✅ Order placed successfully!")
            logger.info(f"Order ID: {order_id}")
            logger.info("\n" + "=" * 60)
            logger.info("CHECK YOUR IBKR TWS:")
            logger.info(f"- Look for order ID: {order_id}")
            logger.info(f"- Symbol: EUR/USD")
            logger.info(f"- Side: {ACTION}")
            logger.info(f"- Quantity: {QUANTITY}")
            logger.info("=" * 60)
            
            # Wait a bit to see order status updates
            logger.info("\nWaiting for order status updates (10 seconds)...")
            await asyncio.sleep(10)
            
            # Check order status
            orders = ibkr.wrapper.orders
            if order_id in orders:
                status = orders[order_id]
                logger.info(f"\nOrder Status:")
                logger.info(f"  Status: {status.get('status')}")
                logger.info(f"  Filled: {status.get('filled')}")
                logger.info(f"  Remaining: {status.get('remaining')}")
                logger.info(f"  Avg Fill Price: {status.get('avg_fill_price')}")
            else:
                logger.info(f"\nNo status updates received yet for order {order_id}")
                logger.info("Check TWS for order status")
            
            # Check positions
            await asyncio.sleep(2)
            ibkr.client.reqPositions()  # Request fresh position data
            await asyncio.sleep(3)
            
            positions = ibkr.get_positions()
            logger.info(f"\nCurrent Positions:")
            if positions:
                for symbol, pos in positions.items():
                    logger.info(f"  {symbol}: {pos}")
            else:
                logger.info("  No positions received yet (may take a moment to update)")
                
        else:
            logger.error("❌ Failed to place order")
            logger.error("Check logs for more details")
            
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        
    finally:
        # Disconnect
        logger.info("\nDisconnecting from IBKR...")
        await ibkr.disconnect()
        logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(test_order_placement())
