# ibkr_streaming/microstructure.py

def compute_microstructure(tick):
    bid = tick["bid"]
    ask = tick["ask"]

    return {
        "spread": ask - bid,
        "mid": tick["mid"]
    }
# This is where we can later add:

# orderflow imbalance

# tick velocity

# volatility bursts

# liquidity shifts