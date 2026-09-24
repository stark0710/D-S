"""
VTOL Lift System Strategy Registry Subsystem

Purpose:
    Defines the `VTOLFiftSystemStrategyRegistry` mapping mission categories
    to specific lift strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.lift_system.lift_system_strategy import (
    LiftSystemStrategy,
    SurveyLiftStrategy,
    CargoLiftStrategy,
    MappingLiftStrategy,
    LongEnduranceLiftStrategy,
    MilitaryLiftStrategy,
    ResearchLiftStrategy,
    BalancedLiftStrategy,
)


class VTOLFiftSystemStrategyRegistry:
    """
    Registry holding vertical lift strategies.
    """

    _registry: Dict[VTOLMissionCategory, LiftSystemStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: LiftSystemStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> LiftSystemStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedLiftStrategy())
VTOLFiftSystemStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedLiftStrategy())
