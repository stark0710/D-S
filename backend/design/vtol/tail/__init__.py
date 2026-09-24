"""
VTOL Tail Sizing Package Entry Point

Purpose:
    Exposes the public models, strategies, layouts, and orchestrator engine
    for the VTOL Tail Sizing Subsystem.
"""

from backend.design.vtol.tail.tail_requirements import TailRequirements
from backend.design.vtol.tail.tail_profile import TailProfile
from backend.design.vtol.tail.tail_constraints import TailConstraints
from backend.design.vtol.tail.tail_geometry import TailGeometry
from backend.design.vtol.tail.tail_structure import TailStructure
from backend.design.vtol.tail.tail_controls import TailControls
from backend.design.vtol.tail.tail_analysis import TailStabilityAnalysis, TailControlAnalysis
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.tail.tail_validator import TailValidator, TailValidationError
from backend.design.vtol.tail.tail_strategy import TailStrategy
from backend.design.vtol.tail.tail_registry import VTOLTailStrategyRegistry
from backend.design.vtol.tail.tail_sizer import TailSizer
from backend.design.vtol.tail.tail_engine import TailEngine
from backend.design.vtol.tail.authoritative_stability import (
    StabilityClassification,
    TrimStatus,
    AuthorityStatus,
    VTailPanelGeometry,
    VTailProjections,
    RuddervatorGeometry,
    AileronGeometry,
    LongitudinalStability,
    DirectionalStability,
    LateralStability,
    ControlDerivatives,
    TrimPoint,
    TrimAnalysis,
    CGEnvelope,
    ControlAuthority,
    AuthoritativeStabilityResult,
    AuthoritativeStabilityEngine,
)

__all__ = [
    "TailRequirements",
    "TailProfile",
    "TailConstraints",
    "TailGeometry",
    "TailStructure",
    "TailControls",
    "TailStabilityAnalysis",
    "TailControlAnalysis",
    "TailResult",
    "TailValidator",
    "TailValidationError",
    "TailStrategy",
    "VTOLTailStrategyRegistry",
    "TailSizer",
    "TailEngine",
    "StabilityClassification",
    "TrimStatus",
    "AuthorityStatus",
    "VTailPanelGeometry",
    "VTailProjections",
    "RuddervatorGeometry",
    "AileronGeometry",
    "LongitudinalStability",
    "DirectionalStability",
    "LateralStability",
    "ControlDerivatives",
    "TrimPoint",
    "TrimAnalysis",
    "CGEnvelope",
    "ControlAuthority",
    "AuthoritativeStabilityResult",
    "AuthoritativeStabilityEngine",
]
