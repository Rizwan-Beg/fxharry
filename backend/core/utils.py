"""Shared helper utilities for the backend services."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable


async def run_in_background(task: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> asyncio.Task[Any]:
    """Schedule a coroutine in the background and return the task handle."""
    loop = asyncio.get_running_loop()
    return loop.create_task(task(*args, **kwargs))
