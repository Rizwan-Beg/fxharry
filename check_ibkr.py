import asyncio
from ib_insync import IB

async def check():
    ib = IB()
    try:
        await ib.connectAsync('127.0.0.1', 7497, clientId=999)
        orders = ib.openOrders()
        positions = ib.positions()
        print(f"Open Orders: {len(orders)}")
        for o in orders:
            print(f"- {o.action} {o.totalQuantity} {o.orderType}")
        print(f"Positions: {len(positions)}")
        for p in positions:
            print(f"- {p.contract.symbol} {p.position}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ib.disconnect()

asyncio.run(check())
