from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .cad_strategy import (
    CADStrategy, SurveyCADStrategy, CargoCADStrategy, MappingCADStrategy,
    LongEnduranceCADStrategy, MilitaryCADStrategy, ResearchCADStrategy, BalancedCADStrategy
)

class CADRegistry:
    """
    Registry mapping mission categories to specific CAD strategy pipelines.
    """
    _registry: Dict[VTOLMissionCategory, Type[CADStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyCADStrategy,
        VTOLMissionCategory.MAPPING: MappingCADStrategy,
        VTOLMissionCategory.CARGO: CargoCADStrategy,
        VTOLMissionCategory.DELIVERY: CargoCADStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceCADStrategy,
        VTOLMissionCategory.MILITARY: MilitaryCADStrategy,
        VTOLMissionCategory.RESEARCH: ResearchCADStrategy,
        VTOLMissionCategory.INSPECTION: BalancedCADStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedCADStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedCADStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedCADStrategy,
        VTOLMissionCategory.CUSTOM: BalancedCADStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> CADStrategy:
        strategy_class = cls._registry.get(category, BalancedCADStrategy)
        return strategy_class()
