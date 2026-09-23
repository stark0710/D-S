"""
Fixed-Wing Aircraft Configuration Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Aircraft Configuration Engineering Framework.
"""

from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)
from backend.design.fixed_wing.configuration.configuration_profile import ConfigurationProfile
from backend.design.fixed_wing.configuration.configuration_constraints import ConfigurationConstraints
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.configuration.configuration_validator import (
    ConfigurationValidator,
    ConfigurationValidationError,
)
from backend.design.fixed_wing.configuration.configuration_strategy import ConfigurationStrategy
from backend.design.fixed_wing.configuration.configuration_registry import ConfigurationStrategyRegistry
from backend.design.fixed_wing.configuration.configuration_scoring import ConfigurationScoringService
from backend.design.fixed_wing.configuration.configuration_selector import ConfigurationSelector
from backend.design.fixed_wing.configuration.configuration_comparator import ConfigurationComparator
from backend.design.fixed_wing.configuration.configuration_recommender import ConfigurationRecommender
from backend.design.fixed_wing.configuration.configuration_engine import ConfigurationEngine

__all__ = [
    "ConfigurationRequirements",
    "WingPosition",
    "PropulsionLayout",
    "TailConfiguration",
    "LandingGearConfiguration",
    "ConfigurationProfile",
    "ConfigurationConstraints",
    "ConfigurationResult",
    "ConfigurationValidator",
    "ConfigurationValidationError",
    "ConfigurationStrategy",
    "ConfigurationStrategyRegistry",
    "ConfigurationScoringService",
    "ConfigurationSelector",
    "ConfigurationComparator",
    "ConfigurationRecommender",
    "ConfigurationEngine",
]
"""
Exposes the main configuration module interface classes.
"""
