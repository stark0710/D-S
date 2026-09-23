"""
Fixed-Wing Manufacturing Strategy Registry Subsystem

Purpose:
    Defines the registry for lookup of manufacturing strategies.

Role in Architecture:
    Enables dynamic strategies selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.manufacturing.manufacturing_strategy import (
    ManufacturingStrategy,
    PrototypeManufacturingStrategy,
    ResearchManufacturingStrategy,
    EducationalManufacturingStrategy,
    LowVolumeProductionStrategy,
    CompositeAircraftStrategy,
    HighPrecisionManufacturingStrategy,
    BalancedManufacturingStrategy,
)


class ManufacturingStrategyRegistry:
    """
    Registry for manufacturing strategies.
    """

    _registry: Dict[str, Type[ManufacturingStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[ManufacturingStrategy]) -> None:
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> ManufacturingStrategy:
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedManufacturingStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._registry.keys())


# Pre-register default manufacturing strategies
ManufacturingStrategyRegistry.register("prototype", PrototypeManufacturingStrategy)
ManufacturingStrategyRegistry.register("research", ResearchManufacturingStrategy)
ManufacturingStrategyRegistry.register("educational", EducationalManufacturingStrategy)
ManufacturingStrategyRegistry.register("low volume production", LowVolumeProductionStrategy)
ManufacturingStrategyRegistry.register("composite aircraft", CompositeAircraftStrategy)
ManufacturingStrategyRegistry.register("high precision", HighPrecisionManufacturingStrategy)
ManufacturingStrategyRegistry.register("balanced", BalancedManufacturingStrategy)
