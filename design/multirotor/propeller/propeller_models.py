from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.motor.motor_result import MotorSpecification
from backend.design.multirotor.propeller.propeller_selector import CatalogPropellerRecord

@dataclass
class PropellerContext(OptimizationContext):
    """
    Multirotor propeller optimization context wrapping mission requirements, strategy, frame, and motor.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    motor_spec: MotorSpecification = None


@dataclass
class PropellerCandidate(OptimizationCandidate):
    """
    Propeller design candidate containing propeller specifications, RPM limits, and tip speeds.
    """
    propeller_record: CatalogPropellerRecord = None
    hover_thrust_n: float = 0.0
    max_thrust_n: float = 0.0
    disc_area_m2: float = 0.0
    disc_loading_n_m2: float = 0.0
    hover_rpm: float = 0.0
    max_rpm: float = 0.0
    tip_speed_m_s: float = 0.0
    hover_power_absorbed_w: float = 0.0
    max_power_absorbed_w: float = 0.0
    hover_efficiency_g_w: float = 0.0
