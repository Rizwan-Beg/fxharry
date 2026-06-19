import vectorbt as vbt
import pandas as pd

close = pd.Series([100, 101, 102, 101, 100])
entries = pd.Series([True, False, False, False, False])
exits = pd.Series([False, False, True, False, False])

# No leverage
pf1 = vbt.Portfolio.from_signals(close, entries, exits, init_cash=1000)
print("No Leverage Profit:", pf1.total_profit())

# 10x Leverage using size and size_type
pf2 = vbt.Portfolio.from_signals(close, entries, exits, init_cash=1000, size=10.0, size_type='percent')
print("10x Leverage Profit:", pf2.total_profit())
