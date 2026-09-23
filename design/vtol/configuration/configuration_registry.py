"""
VTOL Configuration Strategy Registry Subsystem

Purpose:
    Defines the `VTOLConfigurationStrategyRegistry` mapping mission categories
    to specific configuration sizing strategies.
"""

from typing import Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.configuration.configuration_strategy import (
    ConfigurationStrategy,
    SurveyConfigurationStrategy,
    CargoConfigurationStrategy,
    MappingConfigurationStrategy,
    LongEnduranceConfigurationStrategy,
    EmergencyConfigurationStrategy,
    MilitaryConfigurationStrategy,
    ResearchConfigurationStrategy,
    BalancedConfigurationStrategy,
)


class VTOLConfigurationStrategyRegistry:
    """
    Registry for mapping VTOL mission categories to configuration strategies.
    """

    _registry: Dict[VTOLMissionCategory, ConfigurationStrategy] = {}

    @classmethod
    def register(cls, category: VTOLMissionCategory, strategy: ConfigurationStrategy) -> None:
        cls._registry[category] = strategy

    @classmethod
    def get(cls, category: VTOLMissionCategory) -> ConfigurationStrategy:
        return cls._registry.get(category, cls._registry[VTOLMissionCategory.CUSTOM])


# Register default strategy singletons
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.SURVEY, SurveyConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.CARGO, CargoConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.DELIVERY, CargoConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.MAPPING, MappingConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.INSPECTION, SurveyConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.AGRICULTURE, SurveyConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.LONG_ENDURANCE, LongEnduranceConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.EMERGENCY_RESPONSE, EmergencyConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.SEARCH_AND_RESCUE, EmergencyConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.MILITARY, MilitaryConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.RESEARCH, ResearchConfigurationStrategy())
VTOLConfigurationStrategyRegistry.register(VTOLMissionCategory.CUSTOM, BalancedConfigurationStrategy())
