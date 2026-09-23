"""
OptimizationRegistry Subsystem

Purpose:
    Defines the `OptimizationRegistry` class responsible for registering and managing optimization strategies.

Role in Architecture:
    `OptimizationRegistry` provides the plugin registry for optimization strategies.
    It enables dynamic registration of custom optimization strategies without modifying existing pipeline code.
"""

from backend.design.components.optimization.optimization_strategy import OptimizationStrategy


class OptimizationRegistry:
    """
    Registry for managing candidate optimization strategies.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom optimization strategies.
    """

    def __init__(self) -> None:
        """Initializes the OptimizationRegistry."""
        self._strategies: dict[str, OptimizationStrategy] = {}

    def register_strategy(self, strategy: OptimizationStrategy) -> None:
        """
        Registers a new optimization strategy.

        Args:
            strategy (OptimizationStrategy): Strategy instance to register.
        """
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> OptimizationStrategy:
        """
        Retrieves a registered strategy by name.

        Args:
            strategy_name (str): Strategy identifier name.

        Returns:
            OptimizationStrategy: Registered strategy instance.

        Raises:
            KeyError: If strategy_name is not registered.
        """
        if strategy_name not in self._strategies:
            raise KeyError(f"Optimization strategy '{strategy_name}' not found in registry.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[OptimizationStrategy]:
        """Returns a list of all registered OptimizationStrategy instances."""
        return list(self._strategies.values())
