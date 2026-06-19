import vectorbt as vbt
import pandas as pd
import numpy as np

close = pd.Series([100, 101, 102, 101, 100, 105, 110])
entries = pd.Series([True, False, False, True, False, False, False])
exits = pd.Series([False, False, True, False, False, True, False])

pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=1000, fees=0.001, slippage=0.001)

print("total fees paid:", pf.orders.records_readable['Fees'].sum())
print("total slippage?", pf.orders.records_readable)
