"""
Fixed-Wing Wing Strategy Registry Subsystem

Purpose:
    Defines the `WingStrategyRegistry` class to manage registration and retrieval of wing strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.wing.wing_strategy import (
    WingStrategy,
    LongEnduranceWingStrategy,
    SurveillanceWingStrategy,
    SurveyWingStrategy,
    CargoWingStrategy,
    AgricultureWingStrategy,
    TrainingWingStrategy,
    ResearchWingStrategy,
    BalancedWingStrategy,
)


class WingStrategyRegistry:
    """
    Registry for wing design strategies.
    """

    _registry: Dict[str, Type[WingStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[WingStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> WingStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedWingStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default wing strategies
WingStrategyRegistry.register("long endurance", LongEnduranceWingStrategy)
WingStrategyRegistry.register("surveillance", SurveillanceWingStrategy)
WingStrategyRegistry.register("security", SurveillanceWingStrategy)
WingStrategyRegistry.register("inspection", SurveillanceWingStrategy)
WingStrategyRegistry.register("military", SurveillanceWingStrategy)
WingStrategyRegistry.register("mapping", SurveyWingStrategy)  # Survey handles Mapping
WingStrategyRegistry.register("survey", SurveyWingStrategy)
WingStrategyRegistry.register("cargo", CargoWingStrategy)
WingStrategyRegistry.register("agriculture", AgricultureWingStrategy)
WingStrategyRegistry.register("training", TrainingWingStrategy)
WingStrategyRegistry.register("research", ResearchWingStrategy)
WingStrategyRegistry.register("balanced", BalancedWingStrategy)
