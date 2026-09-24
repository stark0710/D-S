"""
CADRegistry Subsystem

Purpose:
    Defines the `CADRegistry` class responsible for registering and managing multirotor CAD generation strategies.

Role in Architecture:
    `CADRegistry` provides the plugin registry for CAD backend generation strategies.
"""

from backend.design.drone.cad.cad_strategy import CADStrategy


class CADRegistry:
    """
    Registry for managing CADStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom CAD platform generation strategies.
    """

    def __init__(self) -> None:
        """Initializes CADRegistry."""
        self._strategies: dict[str, CADStrategy] = {}

    def register_strategy(self, strategy: CADStrategy) -> None:
        """Registers a CADStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> CADStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"CADStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[CADStrategy]:
        """Returns a list of all registered CADStrategy instances."""
        return list(self._strategies.values())
