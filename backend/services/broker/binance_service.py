"""Placeholder for Binance spot/futures integration."""

from .base_broker import BaseBroker


class BinanceService(BaseBroker):
    name = "binance"

    async def connect(self) -> None:
        raise NotImplementedError("Binance connectivity is pending implementation.")

    async def disconnect(self) -> None:
        raise NotImplementedError("Binance disconnect is pending implementation.")

    async def place_order(self, order):
        raise NotImplementedError("Binance order placement is pending implementation.")
