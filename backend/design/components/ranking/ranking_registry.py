"""
RankingRegistry Subsystem

Purpose:
    Defines the `RankingRegistry` class responsible for registering and managing candidate ranking strategies.

Role in Architecture:
    `RankingRegistry` provides the plugin registry for candidate ranking strategies.
    It enables dynamic registration of custom ranking strategies without modifying existing pipeline code.
"""

from backend.design.components.ranking.ranking_strategy import RankingStrategy


class RankingRegistry:
    """
    Registry for managing candidate ranking strategies.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom ranking strategies.
    """

    def __init__(self) -> None:
        """Initializes the RankingRegistry."""
        self._strategies: dict[str, RankingStrategy] = {}

    def register_strategy(self, strategy: RankingStrategy) -> None:
        """
        Registers a new ranking strategy.

        Args:
            strategy (RankingStrategy): Strategy instance to register.
        """
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> RankingStrategy:
        """
        Retrieves a registered strategy by name.

        Args:
            strategy_name (str): Strategy identifier name.

        Returns:
            RankingStrategy: Registered strategy instance.

        Raises:
            KeyError: If strategy_name is not registered.
        """
        if strategy_name not in self._strategies:
            raise KeyError(f"Ranking strategy '{strategy_name}' not found in registry.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[RankingStrategy]:
        """Returns a list of all registered RankingStrategy instances."""
        return list(self._strategies.values())
