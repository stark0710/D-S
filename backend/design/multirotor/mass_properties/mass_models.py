from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.battery.battery_result import PropulsionAssembly
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.layout.layout_result import LayoutSpecification
from backend.design.multirotor.mass_properties.weight_breakdown import WeightBreakdownResult

@dataclass
class MassPropertiesContext(OptimizationContext):
    """
    Multirotor mass properties context wrapping strategy, frame, propulsion, electrical, and layout specs.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    propulsion_assembly: PropulsionAssembly = None
    electrical_spec: ElectricalSpecification = None
    layout_spec: LayoutSpecification = None


@dataclass
class MassPropertiesCandidate(OptimizationCandidate):
    """
    Mass properties design candidate holding weight breakdowns, inertia tensors, and CG offsets.
    """
    weight_breakdown: WeightBreakdownResult = None
    cg_x_m: float = 0.0
    cg_y_m: float = 0.0
    cg_z_m: float = 0.0
    cg_offset_magnitude_m: float = 0.0
    ixx_kg_m2: float = 0.0
    iyy_kg_m2: float = 0.0
    izz_kg_m2: float = 0.0
