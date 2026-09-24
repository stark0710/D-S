"""
Fixed-Wing Tail Strategy Registry Subsystem

Purpose:
    Defines the `TailStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.tail.tail_strategy import (
    TailStrategy,
    LongEnduranceTailStrategy,
    SurveyTailStrategy,
    CargoTailStrategy,
    TrainerTailStrategy,
    AerobaticTailStrategy,
    BalancedTailStrategy,
)


class TailStrategyRegistry:
    """
    Registry for tail design strategies.
    """

    _registry: Dict[str, Type[TailStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[TailStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> TailStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedTailStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default tail strategies
TailStrategyRegistry.register("long endurance", LongEnduranceTailStrategy)
TailStrategyRegistry.register("mapping", SurveyTailStrategy)  # Survey handles Mapping
TailStrategyRegistry.register("survey", SurveyTailStrategy)
TailStrategyRegistry.register("cargo", CargoTailStrategy)
TailStrategyRegistry.register("training", TrainerTailStrategy)
TailStrategyRegistry.register("aerobatic", AerobaticTailStrategy)
TailStrategyRegistry.register("balanced", BalancedTailStrategy)
