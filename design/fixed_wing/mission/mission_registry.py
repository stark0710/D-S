"""
Fixed-Wing Mission Strategy Registry Subsystem

Purpose:
    Defines the `MissionStrategyRegistry` class, which manages registration and lookup of mission strategies.

Role in Architecture:
    Provides a registry to retrieve a concrete `MissionStrategy` instance based on a given `MissionCategory`.
"""

from typing import Dict, Type
from backend.design.fixed_wing.mission.mission_requirements import MissionCategory
from backend.design.fixed_wing.mission.mission_strategy import (
    MissionStrategy,
    SurveyMissionStrategy,
    LongEnduranceMissionStrategy,
    SurveillanceMissionStrategy,
    CargoMissionStrategy,
    AgricultureMissionStrategy,
    ResearchMissionStrategy,
    TrainingMissionStrategy,
    BalancedMissionStrategy,
)


class MissionStrategyRegistry:
    """
    Registry for fixed-wing mission strategies.
    
    Allows strategies to be registered and fetched by their MissionCategory.
    """

    _registry: Dict[MissionCategory, Type[MissionStrategy]] = {}

    @classmethod
    def register(cls, category: MissionCategory, strategy_class: Type[MissionStrategy]) -> None:
        """Registers a strategy class under a specific category."""
        cls._registry[category] = strategy_class

    @classmethod
    def get(cls, category: MissionCategory) -> MissionStrategy:
        """
        Retrieves an instance of the strategy registered for the given category.
        Falls back to BalancedMissionStrategy if not found.
        """
        strategy_class = cls._registry.get(category)
        if strategy_class is None:
            # Fallback or default
            return BalancedMissionStrategy()
        return strategy_class()

    @classmethod
    def list_registered_categories(list_cls) -> list[MissionCategory]:
        """Lists all registered categories."""
        return list(list_cls._registry.keys())


# Pre-register default strategies
MissionStrategyRegistry.register(MissionCategory.SURVEY, SurveyMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.MAPPING, SurveyMissionStrategy)  # Survey handles Mapping too
MissionStrategyRegistry.register(MissionCategory.LONG_ENDURANCE, LongEnduranceMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.SURVEILLANCE, SurveillanceMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.CARGO, CargoMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.AGRICULTURE, AgricultureMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.RESEARCH, ResearchMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.TRAINING, TrainingMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.RACING, BalancedMissionStrategy)
MissionStrategyRegistry.register(MissionCategory.CUSTOM, BalancedMissionStrategy)
