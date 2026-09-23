"""
Fixed-Wing Mission Verification Strategy Registry Subsystem

Purpose:
    Defines the `VerificationStrategyRegistry` class to manage registration and retrieval of strategies.

Role in Architecture:
    Provides dynamic strategy selection based on mission categories or name identifiers.
"""

from typing import Dict, Type
from backend.design.fixed_wing.verification.verification_strategy import (
    VerificationStrategy,
    LongEnduranceVerificationStrategy,
    SurveyVerificationStrategy,
    MappingVerificationStrategy,
    CargoVerificationStrategy,
    TrainerVerificationStrategy,
    ResearchVerificationStrategy,
    BalancedVerificationStrategy,
)


class VerificationStrategyRegistry:
    """
    Registry for design verification strategies.
    """

    _registry: Dict[str, Type[VerificationStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[VerificationStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> VerificationStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedVerificationStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default verification strategies
VerificationStrategyRegistry.register("long endurance", LongEnduranceVerificationStrategy)
VerificationStrategyRegistry.register("mapping", MappingVerificationStrategy)
VerificationStrategyRegistry.register("survey", SurveyVerificationStrategy)
VerificationStrategyRegistry.register("cargo", CargoVerificationStrategy)
VerificationStrategyRegistry.register("training", TrainerVerificationStrategy)
VerificationStrategyRegistry.register("research", ResearchVerificationStrategy)
VerificationStrategyRegistry.register("balanced", BalancedVerificationStrategy)
