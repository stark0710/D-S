"""
PropulsionRegistry Subsystem

Purpose:
    Defines the `PropulsionRegistry` class responsible for registering and managing multirotor propulsion strategies.

Role in Architecture:
    `PropulsionRegistry` provides the plugin registry for propulsion system design strategies.
"""

from backend.design.drone.propulsion.propulsion_strategy import PropulsionStrategy


class PropulsionRegistry:
    """
    Registry for managing PropulsionStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom propulsion design strategies.
    """

    def __init__(self) -> None:
        """Initializes PropulsionRegistry."""
        self._strategies: dict[str, PropulsionStrategy] = {}

    def register_strategy(self, strategy: PropulsionStrategy) -> None:
        """Registers a PropulsionStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> PropulsionStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"PropulsionStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[PropulsionStrategy]:
        """Returns a list of all registered PropulsionStrategy instances."""
        return list(self._strategies.values())
