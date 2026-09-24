from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .manufacturing_strategy import (
    ManufacturingStrategy, PrototypeManufacturingStrategy, LowVolumeManufacturingStrategy,
    ProductionManufacturingStrategy, CompositeManufacturingStrategy, ResearchManufacturingStrategy,
    BalancedManufacturingStrategy
)

class ManufacturingRegistry:
    """
    Registry mapping mission categories to specific manufacturing package strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[ManufacturingStrategy]] = {
        VTOLMissionCategory.SURVEY: PrototypeManufacturingStrategy,
        VTOLMissionCategory.MAPPING: PrototypeManufacturingStrategy,
        VTOLMissionCategory.CARGO: LowVolumeManufacturingStrategy,
        VTOLMissionCategory.DELIVERY: ProductionManufacturingStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: CompositeManufacturingStrategy,
        VTOLMissionCategory.MILITARY: CompositeManufacturingStrategy,
        VTOLMissionCategory.RESEARCH: ResearchManufacturingStrategy,
        VTOLMissionCategory.INSPECTION: BalancedManufacturingStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedManufacturingStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedManufacturingStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedManufacturingStrategy,
        VTOLMissionCategory.CUSTOM: BalancedManufacturingStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> ManufacturingStrategy:
        strategy_class = cls._registry.get(category, BalancedManufacturingStrategy)
        return strategy_class()
