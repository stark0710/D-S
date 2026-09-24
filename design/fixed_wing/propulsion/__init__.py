"""
Fixed-Wing Propulsion Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Propulsion Engineering Framework.
"""

from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements, PropulsionType, PropulsionLayout
from backend.design.fixed_wing.propulsion.propulsion_profile import PropulsionProfile
from backend.design.fixed_wing.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidator, PropulsionValidationError
from backend.design.fixed_wing.propulsion.motor_selector import MotorSelector, MotorRecord
from backend.design.fixed_wing.propulsion.engine_selector import EngineSelector, EngineRecord
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerSelector, PropellerRecord
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.propulsion.propulsion_strategy import PropulsionStrategy
from backend.design.fixed_wing.propulsion.propulsion_registry import PropulsionStrategyRegistry
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine

__all__ = [
    "PropulsionRequirements",
    "PropulsionType",
    "PropulsionLayout",
    "PropulsionProfile",
    "PropulsionConstraints",
    "PropulsionResult",
    "PropulsionValidator",
    "PropulsionValidationError",
    "MotorSelector",
    "MotorRecord",
    "EngineSelector",
    "EngineRecord",
    "PropellerSelector",
    "PropellerRecord",
    "ThrustAnalysis",
    "PowerAnalysis",
    "EfficiencyAnalysis",
    "CruiseAnalysis",
    "ClimbAnalysis",
    "TakeoffAnalysis",
    "PropulsionStrategy",
    "PropulsionStrategyRegistry",
    "PropulsionEngine",
]
"""
Fixed-Wing Propulsion Engineering Framework Entry Point.
"""
