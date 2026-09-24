"""
FrameRegistry Subsystem

Purpose:
    Defines the `FrameRegistry` class responsible for registering and managing multirotor structural frame strategies.

Role in Architecture:
    `FrameRegistry` provides the plugin registry for structural frame design strategies.
"""

from backend.design.drone.structure.frame_strategy import FrameStrategy


class FrameRegistry:
    """
    Registry for managing FrameStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom frame design strategies.
    """

    def __init__(self) -> None:
        """Initializes FrameRegistry."""
        self._strategies: dict[str, FrameStrategy] = {}

    def register_strategy(self, strategy: FrameStrategy) -> None:
        """Registers a FrameStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> FrameStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"FrameStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[FrameStrategy]:
        """Returns a list of all registered FrameStrategy instances."""
        return list(self._strategies.values())
