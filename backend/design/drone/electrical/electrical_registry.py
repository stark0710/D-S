"""
ElectricalRegistry Subsystem

Purpose:
    Defines the `ElectricalRegistry` class responsible for registering and managing multirotor electrical power strategies.

Role in Architecture:
    `ElectricalRegistry` provides the plugin registry for electrical power subsystem design strategies.
"""

from backend.design.drone.electrical.electrical_strategy import ElectricalStrategy


class ElectricalRegistry:
    """
    Registry for managing ElectricalStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom electrical strategies.
    """

    def __init__(self) -> None:
        """Initializes ElectricalRegistry."""
        self._strategies: dict[str, ElectricalStrategy] = {}

    def register_strategy(self, strategy: ElectricalStrategy) -> None:
        """Registers an ElectricalStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> ElectricalStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"ElectricalStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[ElectricalStrategy]:
        """Returns a list of all registered ElectricalStrategy instances."""
        return list(self._strategies.values())
