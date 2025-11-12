"""Abstract base class for broker integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseBroker(ABC):
    """Define the common interface for broker connectivity layers."""

    name: str = "base"

    @abstractmethod
    async def connect(self) -> None:
        """Establish broker connectivity and authentication."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down any open sessions or sockets."""

    @abstractmethod
    async def place_order(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Submit an order to the broker and return execution metadata."""

    async def health(self) -> Dict[str, Any]:
        """Return broker health diagnostics."""
        return {
            "name": self.name,
            "status": "unknown"
        }
