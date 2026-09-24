"""
Fixed-Wing Avionics Strategy Registry Subsystem

Purpose:
    Defines the `AvionicsStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.avionics.avionics_strategy import (
    AvionicsStrategy,
    LongEnduranceAvionicsStrategy,
    SurveyAvionicsStrategy,
    CargoAvionicsStrategy,
    TrainerAvionicsStrategy,
    BVLOSAvionicsStrategy,
    ResearchAvionicsStrategy,
    BalancedAvionicsStrategy,
)


class AvionicsStrategyRegistry:
    """
    Registry for avionics design strategies.
    """

    _registry: Dict[str, Type[AvionicsStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[AvionicsStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> AvionicsStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedAvionicsStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default avionics strategies
AvionicsStrategyRegistry.register("long endurance", LongEnduranceAvionicsStrategy)
AvionicsStrategyRegistry.register("mapping", SurveyAvionicsStrategy)  # Survey handles Mapping
AvionicsStrategyRegistry.register("survey", SurveyAvionicsStrategy)
AvionicsStrategyRegistry.register("cargo", CargoAvionicsStrategy)
AvionicsStrategyRegistry.register("training", TrainerAvionicsStrategy)
AvionicsStrategyRegistry.register("bvlos", BVLOSAvionicsStrategy)
AvionicsStrategyRegistry.register("research", ResearchAvionicsStrategy)
AvionicsStrategyRegistry.register("balanced", BalancedAvionicsStrategy)
