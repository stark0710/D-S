"""
Fixed-Wing Flight Performance Engineering Framework Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Flight Performance Sizing Framework.
"""

from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_profile import FlightProfile
from backend.design.fixed_wing.flight_performance.flight_constraints import FlightConstraints
from backend.design.fixed_wing.flight_performance.flight_result import FlightResult
from backend.design.fixed_wing.flight_performance.flight_validator import FlightValidator, FlightValidationError
from backend.design.fixed_wing.flight_performance.environment_model import EnvironmentModel
from backend.design.fixed_wing.flight_performance.aerodynamic_analysis import AerodynamicAnalysis
from backend.design.fixed_wing.flight_performance.performance_analysis import PerformanceAnalysis
from backend.design.fixed_wing.flight_performance.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.flight_performance.landing_analysis import LandingAnalysis
from backend.design.fixed_wing.flight_performance.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.flight_performance.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.flight_performance.descent_analysis import DescentAnalysis
from backend.design.fixed_wing.flight_performance.stall_analysis import StallAnalysis
from backend.design.fixed_wing.flight_performance.glide_analysis import GlideAnalysis
from backend.design.fixed_wing.flight_performance.turn_performance import TurnAnalysis
from backend.design.fixed_wing.flight_performance.range_analysis import RangeAnalysis
from backend.design.fixed_wing.flight_performance.endurance_analysis import EnduranceAnalysis
from backend.design.fixed_wing.flight_performance.ceiling_analysis import CeilingAnalysis
from backend.design.fixed_wing.flight_performance.stability_analysis import StabilityAnalysis
from backend.design.fixed_wing.flight_performance.maneuver_analysis import ManeuverAnalysis
from backend.design.fixed_wing.flight_performance.mission_performance import MissionPerformance
from backend.design.fixed_wing.flight_performance.flight_strategy import FlightStrategy
from backend.design.fixed_wing.flight_performance.flight_registry import FlightStrategyRegistry
from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine

__all__ = [
    "FlightRequirements",
    "FlightProfile",
    "FlightConstraints",
    "FlightResult",
    "FlightValidator",
    "FlightValidationError",
    "EnvironmentModel",
    "AerodynamicAnalysis",
    "PerformanceAnalysis",
    "TakeoffAnalysis",
    "LandingAnalysis",
    "ClimbAnalysis",
    "CruiseAnalysis",
    "DescentAnalysis",
    "StallAnalysis",
    "GlideAnalysis",
    "TurnAnalysis",
    "RangeAnalysis",
    "EnduranceAnalysis",
    "CeilingAnalysis",
    "StabilityAnalysis",
    "ManeuverAnalysis",
    "MissionPerformance",
    "FlightStrategy",
    "FlightStrategyRegistry",
    "FlightPerformanceEngine",
]
