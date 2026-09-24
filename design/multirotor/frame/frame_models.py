from dataclasses import dataclass, field
from typing import Any, Dict
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_geometry import FrameGeometry

@dataclass
class FrameContext(OptimizationContext):
    """
    Multirotor frame optimization context wrapping mission requirements and strategy.
    """
    strategy_spec: MissionStrategySpecification = None
    payload_weight_kg: float = 0.0
    payload_dimensions_m: tuple[float, float, float] = (0.1, 0.1, 0.1)


@dataclass
class FrameCandidate(OptimizationCandidate):
    """
    Frame design candidate containing wheelbase, arm size, coordinates, and evaluated constraints status.
    """
    geometry: FrameGeometry = None
    frame_mass_kg: float = 0.0
    structural_margin: float = 0.0
    prop_clearance_passed: bool = True
    ground_clearance_passed: bool = True
    payload_fit_passed: bool = True
    size_limit_passed: bool = True
    safety_margin_passed: bool = True
