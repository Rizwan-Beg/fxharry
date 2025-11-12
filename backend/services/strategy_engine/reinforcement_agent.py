"""Reinforcement learning agent scaffolding for trading."""

from typing import Any, Dict


class ReinforcementLearningAgent:
    """Coordinate RL policy evaluation and training loops."""

    def __init__(self, policy: Any | None = None) -> None:
        self.policy = policy

    async def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("RL action selection not yet implemented.")

    async def learn(self, experience: Dict[str, Any]) -> None:
        raise NotImplementedError("RL learning step not yet implemented.")
