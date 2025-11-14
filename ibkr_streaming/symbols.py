# ibkr_streaming/symbols.py

from ib_async import Forex, Contract

# XAUUSD (Gold) - defined as CASH contract (forex-style)
# Symbol should be "XAU" with currency "USD" and exchange "IDEALPRO"
# _xauusd = Contract()
# _xauusd.symbol = "XAU"
# _xauusd.secType = "CASH"
# _xauusd.currency = "USD"
# _xauusd.exchange = "IDEALPRO"

_xauusd = Contract()
_xauusd.symbol = "XAU"
_xauusd.secType = "CASH"
_xauusd.currency = "USD"
_xauusd.exchange = "IDEALPRO"

SYMBOLS = {
    "EURUSD": Forex("EURUSD"),
    "GBPUSD": Forex("GBPUSD"),
    "XAUUSD": _xauusd,
    "USDJPY": Forex("USDJPY"),
    "USDCAD": Forex("USDCAD")
}
