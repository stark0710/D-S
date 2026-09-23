"""
PerformanceRegistry Subsystem

Purpose:
    Defines the `PerformanceRegistry` class responsible for registering and managing multirotor flight performance strategies.

Role in Architecture:
    `PerformanceRegistry` provides the plugin registry for flight performance evaluation strategies.
"""

from backend.design.drone.performance.performance_strategy import PerformanceStrategy


class PerformanceRegistry:
    """
    Registry for managing PerformanceStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom performance evaluation strategies.
    """

    def __init__(self) -> None:
        """Initializes PerformanceRegistry."""
        self._strategies: dict[str, PerformanceStrategy] = {}

    def register_strategy(self, strategy: PerformanceStrategy) -> None:
        """Registers a PerformanceStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> PerformanceStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"PerformanceStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[PerformanceStrategy]:
        """Returns a list of all registered PerformanceStrategy instances."""
        return list(self._strategies.values())
