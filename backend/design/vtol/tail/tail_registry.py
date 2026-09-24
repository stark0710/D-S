"""
VTOL Tail Sizing Strategy Registry Subsystem

Purpose:
    Defines the `VTOLTailStrategyRegistry` mapping mission categories
    to specific tail strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.tail.tail_strategy import (
    TailStrategy,
    SurveyTailStrategy,
    CargoTailStrategy,
    MappingTailStrategy,
    LongEnduranceTailStrategy,
    MilitaryTailStrategy,
    ResearchTailStrategy,
    BalancedTailStrategy,
)


class VTOLTailStrategyRegistry:
    """
    Registry holding tail strategies.
    """

    _registry: Dict[VTOLMissionCategory, TailStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: TailStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> TailStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategies
VTOLTailStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedTailStrategy())
VTOLTailStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedTailStrategy())
