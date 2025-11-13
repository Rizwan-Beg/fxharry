"""Placeholder for OANDA REST/V20 integration."""

from .base_broker import BaseBroker


class OANDAService(BaseBroker):
    name = "oanda"

    async def connect(self) -> None:
        raise NotImplementedError("OANDA connectivity is pending implementation.")

    async def disconnect(self) -> None:
        raise NotImplementedError("OANDA disconnect is pending implementation.")

    async def place_order(self, order):
        raise NotImplementedError("OANDA order placement is pending implementation.")
