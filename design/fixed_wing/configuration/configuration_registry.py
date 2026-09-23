"""
Fixed-Wing Aircraft Configuration Strategy Registry Subsystem

Purpose:
    Defines the `ConfigurationStrategyRegistry` class to manage and retrieve strategies.

Role in Architecture:
    Enables dynamic registration and selection of configuration strategies.
"""

from typing import Dict, Type
from backend.design.fixed_wing.configuration.configuration_strategy import (
    ConfigurationStrategy,
    LongEnduranceConfigurationStrategy,
    SurveillanceConfigurationStrategy,
    SurveyConfigurationStrategy,
    CargoConfigurationStrategy,
    AgricultureConfigurationStrategy,
    ResearchConfigurationStrategy,
    TrainingConfigurationStrategy,
    BalancedConfigurationStrategy,
)


class ConfigurationStrategyRegistry:
    """
    Registry to retrieve concrete configuration strategies.
    """

    _registry: Dict[str, Type[ConfigurationStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[ConfigurationStrategy]) -> None:
        """Registers a strategy class under the given name."""
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> ConfigurationStrategy:
        """Retrieves an instance of the strategy by name. Falls back to Balanced if not found."""
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedConfigurationStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Lists all registered strategies."""
        return list(cls._registry.keys())


# Pre-register default configuration strategies
ConfigurationStrategyRegistry.register("long endurance", LongEnduranceConfigurationStrategy)
ConfigurationStrategyRegistry.register("surveillance", SurveillanceConfigurationStrategy)
ConfigurationStrategyRegistry.register("security", SurveillanceConfigurationStrategy)
ConfigurationStrategyRegistry.register("inspection", SurveillanceConfigurationStrategy)
ConfigurationStrategyRegistry.register("military", SurveillanceConfigurationStrategy)
ConfigurationStrategyRegistry.register("mapping", SurveyConfigurationStrategy)  # Survey handles Mapping
ConfigurationStrategyRegistry.register("survey", SurveyConfigurationStrategy)
ConfigurationStrategyRegistry.register("cargo", CargoConfigurationStrategy)
ConfigurationStrategyRegistry.register("agriculture", AgricultureConfigurationStrategy)
ConfigurationStrategyRegistry.register("research", ResearchConfigurationStrategy)
ConfigurationStrategyRegistry.register("training", TrainingConfigurationStrategy)
ConfigurationStrategyRegistry.register("balanced", BalancedConfigurationStrategy)
