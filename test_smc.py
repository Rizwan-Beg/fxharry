import vectorbt as vbt
import pandas as pd
import numpy as np

close = pd.Series(np.random.rand(100) * 100 + 100)
ema200 = vbt.MA.run(close, 200, ewm=True)
ema50 = vbt.MA.run(close, 50, ewm=True)
rsi = vbt.RSI.run(close, 14)

uptrend = (close > ema50.ma) & (ema50.ma > ema200.ma)
discount_zone = rsi.rsi < 40

ema9 = vbt.MA.run(close, 9, ewm=True)
momentum_shift = close.vbt.crossed_above(ema9.ma)

# Check if discount_zone in last 5 periods
recent_discount = discount_zone.rolling(5).sum() > 0

entries = uptrend & recent_discount & momentum_shift
exits = (rsi.rsi > 70) | close.vbt.crossed_below(ema50.ma)

print(entries.sum())
print(exits.sum())
