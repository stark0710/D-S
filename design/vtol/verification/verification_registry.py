from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .verification_strategy import (
    VerificationStrategy, SurveyVerificationStrategy, CargoVerificationStrategy,
    MappingVerificationStrategy, LongEnduranceVerificationStrategy,
    MilitaryVerificationStrategy, ResearchVerificationStrategy, BalancedVerificationStrategy
)

class VerificationRegistry:
    """
    Registry mapping mission categories to complete flight verification strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[VerificationStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyVerificationStrategy,
        VTOLMissionCategory.MAPPING: MappingVerificationStrategy,
        VTOLMissionCategory.CARGO: CargoVerificationStrategy,
        VTOLMissionCategory.DELIVERY: CargoVerificationStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceVerificationStrategy,
        VTOLMissionCategory.MILITARY: MilitaryVerificationStrategy,
        VTOLMissionCategory.RESEARCH: ResearchVerificationStrategy,
        VTOLMissionCategory.INSPECTION: BalancedVerificationStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedVerificationStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedVerificationStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedVerificationStrategy,
        VTOLMissionCategory.CUSTOM: BalancedVerificationStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> VerificationStrategy:
        strategy_class = cls._registry.get(category, BalancedVerificationStrategy)
        return strategy_class()
