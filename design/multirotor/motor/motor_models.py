from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.motor.motor_selector import CatalogMotorRecord

@dataclass
class MotorContext(OptimizationContext):
    """
    Multirotor motor optimization context wrapping mission requirements, strategy, and frame geometry.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None


@dataclass
class MotorCandidate(OptimizationCandidate):
    """
    Motor design candidate containing motor catalog specifications, current loading, and thermal evaluations.
    """
    motor_record: CatalogMotorRecord = None
    estimated_auw_kg: float = 0.0
    hover_thrust_n: float = 0.0
    max_thrust_n: float = 0.0
    hover_current_a: float = 0.0
    max_current_a: float = 0.0
    hover_power_w: float = 0.0
    motor_efficiency: float = 0.0
    throttle_hover_pct: float = 0.0
