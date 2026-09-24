"""
Fixed-Wing Airfoil Strategy Registry Subsystem

Purpose:
    Defines the `AirfoilStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.airfoil.airfoil_strategy import (
    AirfoilStrategy,
    LongEnduranceAirfoilStrategy,
    SurveyAirfoilStrategy,
    CargoAirfoilStrategy,
    TrainerAirfoilStrategy,
    AerobaticAirfoilStrategy,
    BalancedAirfoilStrategy,
)


class AirfoilStrategyRegistry:
    """
    Registry for airfoil design strategies.
    """

    _registry: Dict[str, Type[AirfoilStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[AirfoilStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> AirfoilStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedAirfoilStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default airfoil strategies
AirfoilStrategyRegistry.register("long endurance", LongEnduranceAirfoilStrategy)
AirfoilStrategyRegistry.register("mapping", SurveyAirfoilStrategy)  # Survey handles Mapping
AirfoilStrategyRegistry.register("survey", SurveyAirfoilStrategy)
AirfoilStrategyRegistry.register("cargo", CargoAirfoilStrategy)
AirfoilStrategyRegistry.register("training", TrainerAirfoilStrategy)
AirfoilStrategyRegistry.register("aerobatic", AerobaticAirfoilStrategy)
AirfoilStrategyRegistry.register("balanced", BalancedAirfoilStrategy)
