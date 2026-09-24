"""
VTOL Electrical Strategy Registry Subsystem

Purpose:
    Defines the `VTOLElectricalStrategyRegistry` mapping mission categories
    to specific electrical strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.electrical.electrical_strategy import (
    ElectricalStrategy,
    SurveyElectricalStrategy,
    CargoElectricalStrategy,
    MappingElectricalStrategy,
    LongEnduranceElectricalStrategy,
    MilitaryElectricalStrategy,
    ResearchElectricalStrategy,
    BalancedElectricalStrategy,
)


class VTOLElectricalStrategyRegistry:
    """
    Registry holding electrical sizing strategies.
    """

    _registry: Dict[VTOLMissionCategory, ElectricalStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: ElectricalStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> ElectricalStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedElectricalStrategy())
VTOLElectricalStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedElectricalStrategy())
