"""
Fixed-Wing Tail (Empennage) Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Tail Engineering Framework.
"""

from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_profile import TailProfile
from backend.design.fixed_wing.tail.tail_constraints import TailConstraints
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis, TailAnalysisService
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.tail_validator import TailValidator, TailValidationError
from backend.design.fixed_wing.tail.tail_strategy import TailStrategy
from backend.design.fixed_wing.tail.tail_registry import TailStrategyRegistry
from backend.design.fixed_wing.tail.tail_sizer import TailSizer
from backend.design.fixed_wing.tail.tail_engine import TailEngine

__all__ = [
    "TailRequirements",
    "TailConfigType",
    "TailProfile",
    "TailConstraints",
    "HorizontalTail",
    "VerticalTail",
    "ControlSurfaces",
    "TailAnalysis",
    "TailAnalysisService",
    "TailResult",
    "TailValidator",
    "TailValidationError",
    "TailStrategy",
    "TailStrategyRegistry",
    "TailSizer",
    "TailEngine",
]
