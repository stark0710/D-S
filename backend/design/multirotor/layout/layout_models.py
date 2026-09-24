from dataclasses import dataclass, field
from typing import Dict, List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.battery.battery_result import PropulsionAssembly
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.layout.component_packager import BoundingBox3D

@dataclass
class LayoutContext(OptimizationContext):
    """
    Multirotor physical layout context wrapping strategy, frame, propulsion, and electrical specs.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    propulsion_assembly: PropulsionAssembly = None
    electrical_spec: ElectricalSpecification = None


@dataclass
class LayoutCandidate(OptimizationCandidate):
    """
    Layout candidate containing 3D coordinates, clearances, bounding boxes, and collision statuses.
    """
    # Envelopes map
    boxes: Dict[str, BoundingBox3D] = field(default_factory=dict)
    
    # Mount methods map
    mounts: Dict[str, str] = field(default_factory=dict)
    
    # Clearance metrics
    fc_to_battery_clearance_m: float = 0.0
    gps_to_pdb_clearance_m: float = 0.0
    packaging_efficiency_pct: float = 0.0
    accessibility_score: float = 0.0
    cg_offset_from_center_m: float = 0.0
