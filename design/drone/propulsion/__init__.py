"""
Drone Propulsion package for Torq Wings Design Studio Phase 5.4 Drone Design Studio.
"""

from backend.design.drone.propulsion.thrust_analysis import ThrustAnalysis, ThrustAnalysisResult
from backend.design.drone.propulsion.power_analysis import PowerAnalysis, PowerAnalysisResult
from backend.design.drone.propulsion.hover_analysis import HoverAnalysis, HoverAnalysisResult
from backend.design.drone.propulsion.efficiency_analysis import EfficiencyAnalysis, EfficiencyAnalysisResult
from backend.design.drone.propulsion.motor_selector import MotorSelector
from backend.design.drone.propulsion.propeller_selector import PropellerSelector
from backend.design.drone.propulsion.propulsion_profile import PropulsionProfile
from backend.design.drone.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.drone.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.propulsion.propulsion_validator import PropulsionValidator
from backend.design.drone.propulsion.propulsion_strategy import (
    PropulsionStrategy,
    BalancedStrategy,
    LongEnduranceStrategy,
    HeavyLiftStrategy,
)
from backend.design.drone.propulsion.propulsion_registry import PropulsionRegistry
from backend.design.drone.propulsion.propulsion_engine import PropulsionEngine

__all__ = [
    "ThrustAnalysis",
    "ThrustAnalysisResult",
    "PowerAnalysis",
    "PowerAnalysisResult",
    "HoverAnalysis",
    "HoverAnalysisResult",
    "EfficiencyAnalysis",
    "EfficiencyAnalysisResult",
    "MotorSelector",
    "PropellerSelector",
    "PropulsionProfile",
    "PropulsionRequirements",
    "PropulsionConstraints",
    "PropulsionResult",
    "PropulsionValidator",
    "PropulsionStrategy",
    "BalancedStrategy",
    "LongEnduranceStrategy",
    "HeavyLiftStrategy",
    "PropulsionRegistry",
    "PropulsionEngine",
]
