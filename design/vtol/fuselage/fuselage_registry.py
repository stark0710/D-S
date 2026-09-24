"""
VTOL Fuselage Sizing Strategy Registry Subsystem

Purpose:
    Defines the `VTOLFuselageStrategyRegistry` mapping mission categories
    to specific fuselage strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.fuselage.fuselage_strategy import (
    FuselageStrategy,
    SurveyFuselageStrategy,
    CargoFuselageStrategy,
    MappingFuselageStrategy,
    LongEnduranceFuselageStrategy,
    MilitaryFuselageStrategy,
    ResearchFuselageStrategy,
    BalancedFuselageStrategy,
)


class VTOLFuselageStrategyRegistry:
    """
    Registry holding fuselage strategies.
    """

    _registry: Dict[VTOLMissionCategory, FuselageStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: FuselageStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> FuselageStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedFuselageStrategy())
VTOLFuselageStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedFuselageStrategy())
