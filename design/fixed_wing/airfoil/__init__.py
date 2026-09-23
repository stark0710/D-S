"""
Fixed-Wing Airfoil Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Airfoil Engineering Framework.
"""

from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements, AirfoilType
from backend.design.fixed_wing.airfoil.airfoil_profile import AirfoilProfile
from backend.design.fixed_wing.airfoil.airfoil_constraints import AirfoilConstraints
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.airfoil.airfoil_validator import AirfoilValidator, AirfoilValidationError
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilDatabase, AirfoilRecord
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis, ReynoldsAnalysisService
from backend.design.fixed_wing.airfoil.polar_analysis import PolarData, PolarAnalysisService
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMap, PerformanceMapService
from backend.design.fixed_wing.airfoil.airfoil_analysis import AirfoilAnalysis, AirfoilAnalysisService
from backend.design.fixed_wing.airfoil.airfoil_strategy import AirfoilStrategy
from backend.design.fixed_wing.airfoil.airfoil_registry import AirfoilStrategyRegistry
from backend.design.fixed_wing.airfoil.airfoil_selector import AirfoilSelector
from backend.design.fixed_wing.airfoil.airfoil_engine import AirfoilEngine

__all__ = [
    "AirfoilRequirements",
    "AirfoilType",
    "AirfoilProfile",
    "AirfoilConstraints",
    "AirfoilResult",
    "AirfoilValidator",
    "AirfoilValidationError",
    "AirfoilDatabase",
    "AirfoilRecord",
    "ReynoldsAnalysis",
    "ReynoldsAnalysisService",
    "PolarData",
    "PolarAnalysisService",
    "PerformanceMap",
    "PerformanceMapService",
    "AirfoilAnalysis",
    "AirfoilAnalysisService",
    "AirfoilStrategy",
    "AirfoilStrategyRegistry",
    "AirfoilSelector",
    "AirfoilEngine",
]
