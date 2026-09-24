"""
OptimizationRegistry Subsystem

Purpose:
    Defines the `OptimizationRegistry` class responsible for registering and managing multirotor design optimization strategies.

Role in Architecture:
    `OptimizationRegistry` provides the plugin registry for design optimization strategies.
"""

from backend.design.drone.optimization.optimization_strategy import OptimizationStrategy


class OptimizationRegistry:
    """
    Registry for managing OptimizationStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom design optimization strategies.
    """

    def __init__(self) -> None:
        """Initializes OptimizationRegistry."""
        self._strategies: dict[str, OptimizationStrategy] = {}

    def register_strategy(self, strategy: OptimizationStrategy) -> None:
        """Registers an OptimizationStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> OptimizationStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"OptimizationStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[OptimizationStrategy]:
        """Returns a list of all registered OptimizationStrategy instances."""
        return list(self._strategies.values())
