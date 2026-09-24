from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .hover_strategy import (
    HoverStrategy, SurveyHoverStrategy, CargoHoverStrategy, MappingHoverStrategy,
    LongEnduranceHoverStrategy, MilitaryHoverStrategy, ResearchHoverStrategy, BalancedHoverStrategy
)

class HoverRegistry:
    """
    Registry mapping mission categories to specific hover strategy configurations.
    """
    _registry: Dict[VTOLMissionCategory, Type[HoverStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyHoverStrategy,
        VTOLMissionCategory.MAPPING: MappingHoverStrategy,
        VTOLMissionCategory.CARGO: CargoHoverStrategy,
        VTOLMissionCategory.DELIVERY: CargoHoverStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceHoverStrategy,
        VTOLMissionCategory.MILITARY: MilitaryHoverStrategy,
        VTOLMissionCategory.RESEARCH: ResearchHoverStrategy,
        VTOLMissionCategory.INSPECTION: BalancedHoverStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedHoverStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedHoverStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedHoverStrategy,
        VTOLMissionCategory.CUSTOM: BalancedHoverStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> HoverStrategy:
        strategy_class = cls._registry.get(category, BalancedHoverStrategy)
        return strategy_class()
