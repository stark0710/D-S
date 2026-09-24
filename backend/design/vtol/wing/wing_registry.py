"""
VTOL Wing Sizing Strategy Registry Subsystem

Purpose:
    Defines the `VTOLWingStrategyRegistry` mapping mission categories
    to wing strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.wing.wing_strategy import (
    WingStrategy,
    SurveyWingStrategy,
    CargoWingStrategy,
    MappingWingStrategy,
    LongEnduranceWingStrategy,
    MilitaryWingStrategy,
    ResearchWingStrategy,
    BalancedWingStrategy,
)


class VTOLWingStrategyRegistry:
    """
    Registry for wing strategies.
    """

    _registry: Dict[VTOLMissionCategory, WingStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: WingStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> WingStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register defaults
VTOLWingStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedWingStrategy())
VTOLWingStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedWingStrategy())
