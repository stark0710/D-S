"""
Fixed-Wing Payload Strategy Registry Subsystem

Purpose:
    Defines the `PayloadStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.payload.payload_strategy import (
    PayloadStrategy,
    LongEndurancePayloadStrategy,
    SurveillancePayloadStrategy,
    SurveyPayloadStrategy,
    MappingPayloadStrategy,
    InspectionPayloadStrategy,
    CargoPayloadStrategy,
    ResearchPayloadStrategy,
    AgriculturePayloadStrategy,
    EnvironmentalPayloadStrategy,
    BalancedPayloadStrategy,
)


class PayloadStrategyRegistry:
    """
    Registry for payload integration strategies.
    """

    _registry: Dict[str, Type[PayloadStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[PayloadStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> PayloadStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedPayloadStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default payload strategies
PayloadStrategyRegistry.register("long endurance", LongEndurancePayloadStrategy)
PayloadStrategyRegistry.register("surveillance", SurveillancePayloadStrategy)
PayloadStrategyRegistry.register("security", SurveillancePayloadStrategy)
PayloadStrategyRegistry.register("military", SurveillancePayloadStrategy)
PayloadStrategyRegistry.register("mapping", MappingPayloadStrategy)
PayloadStrategyRegistry.register("survey", SurveyPayloadStrategy)
PayloadStrategyRegistry.register("inspection", InspectionPayloadStrategy)
PayloadStrategyRegistry.register("cargo", CargoPayloadStrategy)
PayloadStrategyRegistry.register("research", ResearchPayloadStrategy)
PayloadStrategyRegistry.register("agriculture", AgriculturePayloadStrategy)
PayloadStrategyRegistry.register("environmental", EnvironmentalPayloadStrategy)
PayloadStrategyRegistry.register("balanced", BalancedPayloadStrategy)
