#!/usr/bin/env python3
"""
Test script to place EUR/USD order using ib_async library
Following the pattern from Interactive_Brokers_firststeps.ipynb
"""
import pandas as pd
from ib_async import *

def main():
    print("=" * 60)
    print("Testing IBKR Order Placement with ib_async")
    print("=" * 60)
    
    # Start event loop (required for ib_async)
    util.startLoop()
    
    # Create IB connection
    ib = IB()
    
    try:
        # Connect to IBKR TWS/Gateway
        # Port 7497 = Paper Trading
        print("\n[1] Connecting to IBKR TWS on port 7497...")
        ib.connect('127.0.0.1', 7497, clientId=999)
        print("✅ Connected successfully!")
        
        # Create EUR/USD CFD contract (as shown in the notebook)
        print("\n[2] Creating EUR/USD CFD contract...")
        contract = CFD("EUR", currency="USD")
        print(f"Contract: {contract}")
        
        # Qualify the contract
        print("\n[3] Qualifying contract with IBKR...")
        ib.qualifyContracts(contract)
        print(f"Qualified contract: {contract}")
        
        # Create Market Buy Order for 1000 units
        print("\n[4] Creating Market BUY order for 1000 units...")
        order = MarketOrder(action="BUY", totalQuantity=1000)
        print(f"Order: {order}")
        
        # Place the order
        print("\n[5] Placing order...")
        trade = ib.placeOrder(contract, order)
        print(f"✅ Order placed!")
        print(f"Trade object: {trade}")
        
        # Wait for order to be processed
        print("\n[6] Waiting for order to be filled (10 seconds)...")
        ib.sleep(10)
        
        # Check trade status
        print("\n" + "=" * 60)
        print("ORDER STATUS:")
        print("=" * 60)
        print(f"Trade: {trade}")
        print(f"Order Status: {trade.orderStatus.status}")
        print(f"Filled Quantity: {trade.orderStatus.filled}")
        print(f"Remaining: {trade.orderStatus.remaining}")
        print(f"Avg Fill Price: {trade.orderStatus.avgFillPrice}")
        
        # Display trade log
        print("\n" + "=" * 60)
        print("TRADE LOG:")
        print("=" * 60)
        for log_entry in trade.log:
            print(f"  {log_entry}")
        
        # Check all trades
        print("\n" + "=" * 60)
        print("ALL TRADES:")
        print("=" * 60)
        all_trades = ib.trades()
        for t in all_trades:
            print(f"  {t}")
        
        # Check positions
        print("\n" + "=" * 60)
        print("CURRENT POSITIONS:")
        print("=" * 60)
        positions = ib.positions()
        if positions:
            for pos in positions:
                print(f"  Account: {pos.account}")
                print(f"  Contract: {pos.contract.symbol} ({pos.contract.currency})")
                print(f"  Position: {pos.position}")
                print(f"  Avg Cost: {pos.avgCost}")
                print("-" * 40)
        else:
            print("  No positions found")
        
        # Check fills
        print("\n" + "=" * 60)
        print("ORDER FILLS:")
        print("=" * 60)
        fills = ib.fills()
        if fills:
            for fill in fills:
                print(f"  Execution ID: {fill.execution.execId}")
                print(f"  Time: {fill.execution.time}")
                print(f"  Side: {fill.execution.side}")
                print(f"  Quantity: {fill.execution.cumQty}")
                print(f"  Price: {fill.execution.avgPrice}")
                print("-" * 40)
        else:
            print("  No fills yet")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED!")
        print("=" * 60)
        print("\nNOW CHECK YOUR IBKR TWS:")
        print("1. Go to 'Order Management' tab")
        print("2. Look for EUR.USD CFD order")
        print("3. Check 'Portfolio' for EUR position")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect
        print("\n[7] Disconnecting from IBKR...")
        ib.disconnect()
        print("✅ Disconnected")

if __name__ == "__main__":
    main()
