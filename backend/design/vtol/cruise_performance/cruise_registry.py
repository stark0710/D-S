from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .cruise_strategy import (
    CruisePerformanceStrategy, SurveyCruisePerformanceStrategy, CargoCruisePerformanceStrategy,
    MappingCruisePerformanceStrategy, LongEnduranceCruisePerformanceStrategy,
    MilitaryCruisePerformanceStrategy, ResearchCruisePerformanceStrategy, BalancedCruisePerformanceStrategy
)

class CruiseRegistry:
    """
    Registry mapping mission categories to forward flight cruise strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[CruisePerformanceStrategy]] = {
        VTOLMissionCategory.SURVEY: SurveyCruisePerformanceStrategy,
        VTOLMissionCategory.MAPPING: MappingCruisePerformanceStrategy,
        VTOLMissionCategory.CARGO: CargoCruisePerformanceStrategy,
        VTOLMissionCategory.DELIVERY: CargoCruisePerformanceStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: LongEnduranceCruisePerformanceStrategy,
        VTOLMissionCategory.MILITARY: MilitaryCruisePerformanceStrategy,
        VTOLMissionCategory.RESEARCH: ResearchCruisePerformanceStrategy,
        VTOLMissionCategory.INSPECTION: BalancedCruisePerformanceStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedCruisePerformanceStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedCruisePerformanceStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedCruisePerformanceStrategy,
        VTOLMissionCategory.CUSTOM: BalancedCruisePerformanceStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> CruisePerformanceStrategy:
        strategy_class = cls._registry.get(category, BalancedCruisePerformanceStrategy)
        return strategy_class()
