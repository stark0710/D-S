from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .payload_strategy import (
    PayloadStrategy, SurveyPayloadStrategy, CargoPayloadStrategy, MappingPayloadStrategy,
    AgriculturePayloadStrategy, EmergencyPayloadStrategy, MilitaryPayloadStrategy, ResearchPayloadStrategy, BalancedPayloadStrategy
)

class PayloadRegistry:
    """
    Registry mapping mission categories to specific payload sizing strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[PayloadStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyPayloadStrategy,
        VTOLMissionCategory.MAPPING: MappingPayloadStrategy,
        VTOLMissionCategory.CARGO: CargoPayloadStrategy,
        VTOLMissionCategory.DELIVERY: CargoPayloadStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: SurveyPayloadStrategy, # Fallback
        VTOLMissionCategory.MILITARY: MilitaryPayloadStrategy,
        VTOLMissionCategory.RESEARCH: ResearchPayloadStrategy,
        VTOLMissionCategory.INSPECTION: BalancedPayloadStrategy,
        VTOLMissionCategory.AGRICULTURE: AgriculturePayloadStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: EmergencyPayloadStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: EmergencyPayloadStrategy,
        VTOLMissionCategory.CUSTOM: BalancedPayloadStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> PayloadStrategy:
        strategy_class = cls._registry.get(category, BalancedPayloadStrategy)
        return strategy_class()
