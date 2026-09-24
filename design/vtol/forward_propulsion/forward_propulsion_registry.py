"""
VTOL Forward Propulsion Strategy Registry Subsystem

Purpose:
    Defines the `VTOLForwardPropulsionStrategyRegistry` mapping mission categories
    to specific forward strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.forward_propulsion.forward_propulsion_strategy import (
    ForwardPropulsionStrategy,
    SurveyCruiseStrategy,
    CargoCruiseStrategy,
    MappingCruiseStrategy,
    LongEnduranceCruiseStrategy,
    MilitaryCruiseStrategy,
    ResearchCruiseStrategy,
    BalancedCruiseStrategy,
)


class VTOLForwardPropulsionStrategyRegistry:
    """
    Registry holding forward propulsion strategies.
    """

    _registry: Dict[VTOLMissionCategory, ForwardPropulsionStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: ForwardPropulsionStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> ForwardPropulsionStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, BalancedCruiseStrategy())
VTOLForwardPropulsionStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, BalancedCruiseStrategy())
