"""
VTOL Airfoil Sizing Strategy Registry Subsystem

Purpose:
    Defines the `VTOLAirfoilStrategyRegistry` mapping mission categories
    to specific airfoil design strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.airfoil.airfoil_strategy import (
    AirfoilStrategy,
    SurveyAirfoilStrategy,
    CargoAirfoilStrategy,
    MappingAirfoilStrategy,
    LongEnduranceAirfoilStrategy,
    MilitaryAirfoilStrategy,
    ResearchAirfoilStrategy,
    BalancedAirfoilStrategy,
)


class VTOLAirfoilStrategyRegistry:
    """
    Registry holding airfoil strategies.
    """

    _registry: Dict[VTOLMissionCategory, AirfoilStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: AirfoilStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> AirfoilStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedAirfoilStrategy())
VTOLAirfoilStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedAirfoilStrategy())
