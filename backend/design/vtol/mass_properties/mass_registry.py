from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .mass_strategy import (
    MassStrategy, SurveyMassStrategy, CargoMassStrategy, MappingMassStrategy,
    LongEnduranceMassStrategy, MilitaryMassStrategy, ResearchMassStrategy, BalancedMassStrategy
)

class MassRegistry:
    """
    Registry mapping mission categories to specific mass strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[MassStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyMassStrategy,
        VTOLMissionCategory.MAPPING: MappingMassStrategy,
        VTOLMissionCategory.CARGO: CargoMassStrategy,
        VTOLMissionCategory.DELIVERY: CargoMassStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceMassStrategy,
        VTOLMissionCategory.MILITARY: MilitaryMassStrategy,
        VTOLMissionCategory.RESEARCH: ResearchMassStrategy,
        VTOLMissionCategory.INSPECTION: BalancedMassStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedMassStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedMassStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedMassStrategy,
        VTOLMissionCategory.CUSTOM: BalancedMassStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> MassStrategy:
        strategy_class = cls._registry.get(category, BalancedMassStrategy)
        return strategy_class()
