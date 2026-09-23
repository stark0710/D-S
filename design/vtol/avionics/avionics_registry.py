from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .avionics_strategy import (
    AvionicsStrategy, SurveyAvionicsStrategy, CargoAvionicsStrategy, MappingAvionicsStrategy,
    LongEnduranceAvionicsStrategy, MilitaryAvionicsStrategy, ResearchAvionicsStrategy, BalancedAvionicsStrategy
)

class AvionicsRegistry:
    """
    Registry mapping mission categories to specific avionics sizing strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[AvionicsStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyAvionicsStrategy,
        VTOLMissionCategory.MAPPING: MappingAvionicsStrategy,
        VTOLMissionCategory.CARGO: CargoAvionicsStrategy,
        VTOLMissionCategory.DELIVERY: CargoAvionicsStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceAvionicsStrategy,
        VTOLMissionCategory.MILITARY: MilitaryAvionicsStrategy,
        VTOLMissionCategory.RESEARCH: ResearchAvionicsStrategy,
        VTOLMissionCategory.INSPECTION: BalancedAvionicsStrategy,
        VTOLMissionCategory.AGRICULTURE: SurveyAvionicsStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedAvionicsStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedAvionicsStrategy,
        VTOLMissionCategory.CUSTOM: BalancedAvionicsStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> AvionicsStrategy:
        strategy_class = cls._registry.get(category, BalancedAvionicsStrategy)
        return strategy_class()
