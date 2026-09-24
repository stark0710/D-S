from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.motor.motor_result import MotorSpecification
from backend.design.multirotor.propeller.propeller_result import PropellerSpecification
from backend.design.multirotor.esc.esc_result import ESCSpecification
from backend.design.multirotor.battery.battery_selector import CatalogBatteryRecord

@dataclass
class BatteryContext(OptimizationContext):
    """
    Multirotor battery optimization context wrapping strategy, frame, motor, propeller, and ESC specifications.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    motor_spec: MotorSpecification = None
    propeller_spec: PropellerSpecification = None
    esc_spec: ESCSpecification = None


@dataclass
class BatteryCandidate(OptimizationCandidate):
    """
    Battery design candidate containing battery component specifications, sizing weights, and flight times.
    """
    battery_record: CatalogBatteryRecord = None
    estimated_auw_kg: float = 0.0
    nominal_voltage_v: float = 0.0
    battery_energy_wh: float = 0.0
    hover_current_draw_a: float = 0.0
    max_current_draw_a: float = 0.0
    continuous_discharge_limit_a: float = 0.0
    burst_discharge_limit_a: float = 0.0
    estimated_hover_time_min: float = 0.0
    estimated_flight_time_min: float = 0.0
    remaining_energy_margin_pct: float = 0.0
