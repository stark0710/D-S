"""
VTOL Mission Strategy Registry Subsystem

Purpose:
    Defines the `VTOLMissionStrategyRegistry` to map mission categories
    to the correct strategy implementation.
"""

from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.mission.mission_strategy import (
    MissionStrategy,
    SurveyMissionStrategy,
    CargoMissionStrategy,
    MappingMissionStrategy,
    LongEnduranceMissionStrategy,
    EmergencyMissionStrategy,
    MilitaryMissionStrategy,
    ResearchMissionStrategy,
    BalancedMissionStrategy,
)


class VTOLMissionStrategyRegistry:
    """
    Registry holding available mission strategies for the VTOL studio.
    """

    _registry: Dict[VTOLMissionCategory, MissionStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: MissionStrategy) -> None:
        """Registers a new strategy with the registry."""
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> MissionStrategy:
        """
        Retrieves the strategy mapped to the category. Falls back to Balanced if unknown.
        """
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Populate default strategies
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, EmergencyMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, EmergencyMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchMissionStrategy())
VTOLMissionStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedMissionStrategy())
