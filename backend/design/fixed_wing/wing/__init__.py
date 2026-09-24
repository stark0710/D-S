"""
Fixed-Wing Wing Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Wing Engineering Framework.
"""

from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_profile import WingProfile
from backend.design.fixed_wing.wing.wing_constraints import WingConstraints
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis, WingAnalysisService
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.wing.wing_validator import WingValidator, WingValidationError
from backend.design.fixed_wing.wing.wing_strategy import WingStrategy
from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
from backend.design.fixed_wing.wing.wing_sizer import WingSizer
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService
from backend.design.fixed_wing.wing.wing_engine import WingEngine

__all__ = [
    "WingRequirements",
    "PlanformType",
    "WingProfile",
    "WingConstraints",
    "WingGeometry",
    "WingAnalysis",
    "WingAnalysisService",
    "WingResult",
    "WingValidator",
    "WingValidationError",
    "WingStrategy",
    "WingStrategyRegistry",
    "WingSizer",
    "PlanformGeometryService",
    "WingEngine",
]
