import vectorbt as vbt
import pandas as pd
import numpy as np

close = pd.Series([100, 101, 102, 101, 100])
entries = pd.Series([True, False, False, False, False])
exits = pd.Series([False, False, True, False, False])

# Calculate size dynamically based on leverage
leverage = 30
size = (1000 * leverage) / close[entries]

pf = vbt.Portfolio.from_signals(
    close, entries, exits, 
    init_cash=1000, 
    size=30, size_type='value' # Wait, size_type=percent maybe?
)
print(pf.total_profit())
