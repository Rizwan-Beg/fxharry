"""Placeholder for MetaTrader 5 bridge integration."""

from .base_broker import BaseBroker


class MT5Service(BaseBroker):
    name = "mt5"

    async def connect(self) -> None:
        raise NotImplementedError("MT5 connectivity is pending implementation.")

    async def disconnect(self) -> None:
        raise NotImplementedError("MT5 disconnect is pending implementation.")

    async def place_order(self, order):
        raise NotImplementedError("MT5 order placement is pending implementation.")
