"""
Fixed-Wing Propulsion Strategy Registry Subsystem

Purpose:
    Defines the `PropulsionStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.propulsion.propulsion_strategy import (
    PropulsionStrategy,
    LongEndurancePropulsionStrategy,
    SurveyPropulsionStrategy,
    CargoPropulsionStrategy,
    TrainerPropulsionStrategy,
    HighSpeedPropulsionStrategy,
    BalancedPropulsionStrategy,
)


class PropulsionStrategyRegistry:
    """
    Registry for propulsion design strategies.
    """

    _registry: Dict[str, Type[PropulsionStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[PropulsionStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> PropulsionStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedPropulsionStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default propulsion strategies
PropulsionStrategyRegistry.register("long endurance", LongEndurancePropulsionStrategy)
PropulsionStrategyRegistry.register("mapping", SurveyPropulsionStrategy)  # Survey handles Mapping
PropulsionStrategyRegistry.register("survey", SurveyPropulsionStrategy)
PropulsionStrategyRegistry.register("cargo", CargoPropulsionStrategy)
PropulsionStrategyRegistry.register("training", TrainerPropulsionStrategy)
PropulsionStrategyRegistry.register("high speed", HighSpeedPropulsionStrategy)
PropulsionStrategyRegistry.register("balanced", BalancedPropulsionStrategy)
