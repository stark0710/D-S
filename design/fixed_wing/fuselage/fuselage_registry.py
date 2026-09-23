"""
Fixed-Wing Fuselage Strategy Registry Subsystem

Purpose:
    Defines the `FuselageStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.fuselage.fuselage_strategy import (
    FuselageStrategy,
    LongEnduranceFuselageStrategy,
    SurveyFuselageStrategy,
    CargoFuselageStrategy,
    AgricultureFuselageStrategy,
    TrainerFuselageStrategy,
    ResearchFuselageStrategy,
    BalancedFuselageStrategy,
)


class FuselageStrategyRegistry:
    """
    Registry for fuselage design strategies.
    """

    _registry: Dict[str, Type[FuselageStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[FuselageStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> FuselageStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedFuselageStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default fuselage strategies
FuselageStrategyRegistry.register("long endurance", LongEnduranceFuselageStrategy)
FuselageStrategyRegistry.register("mapping", SurveyFuselageStrategy)  # Survey handles Mapping
FuselageStrategyRegistry.register("survey", SurveyFuselageStrategy)
FuselageStrategyRegistry.register("cargo", CargoFuselageStrategy)
FuselageStrategyRegistry.register("agriculture", AgricultureFuselageStrategy)
FuselageStrategyRegistry.register("training", TrainerFuselageStrategy)
FuselageStrategyRegistry.register("research", ResearchFuselageStrategy)
FuselageStrategyRegistry.register("balanced", BalancedFuselageStrategy)
