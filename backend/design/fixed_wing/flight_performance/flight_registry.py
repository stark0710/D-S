"""
Fixed-Wing Flight Strategy Registry Subsystem

Purpose:
    Defines the `FlightStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.flight_performance.flight_strategy import (
    FlightStrategy,
    LongEnduranceFlightStrategy,
    SurveyFlightStrategy,
    MappingFlightStrategy,
    CargoFlightStrategy,
    TrainerFlightStrategy,
    HighSpeedFlightStrategy,
    ResearchFlightStrategy,
    BalancedFlightStrategy,
)


class FlightStrategyRegistry:
    """
    Registry for flight performance design strategies.
    """

    _registry: Dict[str, Type[FlightStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[FlightStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> FlightStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedFlightStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default flight strategies
FlightStrategyRegistry.register("long endurance", LongEnduranceFlightStrategy)
FlightStrategyRegistry.register("mapping", MappingFlightStrategy)
FlightStrategyRegistry.register("survey", SurveyFlightStrategy)
FlightStrategyRegistry.register("cargo", CargoFlightStrategy)
FlightStrategyRegistry.register("training", TrainerFlightStrategy)
FlightStrategyRegistry.register("high speed", HighSpeedFlightStrategy)
FlightStrategyRegistry.register("research", ResearchFlightStrategy)
FlightStrategyRegistry.register("balanced", BalancedFlightStrategy)
