"""
Fixed-Wing Mass Strategy Registry Subsystem

Purpose:
    Defines the `MassStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.mass_properties.mass_strategy import (
    MassStrategy,
    LongEnduranceMassStrategy,
    SurveyMassStrategy,
    MappingMassStrategy,
    CargoMassStrategy,
    ResearchMassStrategy,
    TrainerMassStrategy,
    BalancedMassStrategy,
)


class MassStrategyRegistry:
    """
    Registry for mass properties design strategies.
    """

    _registry: Dict[str, Type[MassStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[MassStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> MassStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedMassStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default mass strategies
MassStrategyRegistry.register("long endurance", LongEnduranceMassStrategy)
MassStrategyRegistry.register("mapping", MappingMassStrategy)
MassStrategyRegistry.register("survey", SurveyMassStrategy)
MassStrategyRegistry.register("cargo", CargoMassStrategy)
MassStrategyRegistry.register("research", ResearchMassStrategy)
MassStrategyRegistry.register("training", TrainerMassStrategy)
MassStrategyRegistry.register("balanced", BalancedMassStrategy)
