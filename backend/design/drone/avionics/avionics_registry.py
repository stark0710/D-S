"""
AvionicsRegistry Subsystem

Purpose:
    Defines the `AvionicsRegistry` class responsible for registering and managing multirotor avionics strategies.

Role in Architecture:
    `AvionicsRegistry` provides the plugin registry for avionics architecture design strategies.
"""

from backend.design.drone.avionics.avionics_strategy import AvionicsStrategy


class AvionicsRegistry:
    """
    Registry for managing AvionicsStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom avionics strategies.
    """

    def __init__(self) -> None:
        """Initializes AvionicsRegistry."""
        self._strategies: dict[str, AvionicsStrategy] = {}

    def register_strategy(self, strategy: AvionicsStrategy) -> None:
        """Registers an AvionicsStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> AvionicsStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"AvionicsStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[AvionicsStrategy]:
        """Returns a list of all registered AvionicsStrategy instances."""
        return list(self._strategies.values())
