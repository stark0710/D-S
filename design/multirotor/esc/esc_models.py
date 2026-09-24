from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.motor.motor_result import MotorSpecification
from backend.design.multirotor.propeller.propeller_result import PropellerSpecification
from backend.design.multirotor.esc.esc_selector import CatalogEscRecord

@dataclass
class EscContext(OptimizationContext):
    """
    Multirotor ESC optimization context wrapping mission requirements, strategy, frame, motor, and propeller.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    motor_spec: MotorSpecification = None
    propeller_spec: PropellerSpecification = None


@dataclass
class EscCandidate(OptimizationCandidate):
    """
    ESC design candidate containing ESC catalog specifications, current margins, and thermal ratings.
    """
    esc_record: CatalogEscRecord = None
    hover_current_a: float = 0.0
    max_current_a: float = 0.0
    esc_efficiency: float = 0.0
    hover_power_loss_w: float = 0.0
    max_power_loss_w: float = 0.0
    current_margin_a: float = 0.0
    thermal_margin_pct: float = 0.0
