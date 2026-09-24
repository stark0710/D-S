from dataclasses import dataclass
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.battery.battery_result import PropulsionAssembly
from backend.design.multirotor.electrical.wiring_optimizer import CatalogWireRecord
from backend.design.multirotor.electrical.connector_selector import CatalogConnectorRecord
from backend.design.multirotor.electrical.power_distribution import PowerDistributionBudget

@dataclass
class ElectricalContext(OptimizationContext):
    """
    Multirotor electrical optimization context wrapping strategy, frame, and propulsion assembly.
    """
    strategy_spec: MissionStrategySpecification = None
    frame_spec: FrameSpecification = None
    propulsion_assembly: PropulsionAssembly = None


@dataclass
class ElectricalCandidate(OptimizationCandidate):
    """
    Electrical design candidate containing sized wires, connectors, and power budgets.
    """
    # Sized main wiring
    main_wire: CatalogWireRecord = None
    esc_wire: CatalogWireRecord = None
    motor_wire: CatalogWireRecord = None
    
    # Sized connectors
    battery_connector: CatalogConnectorRecord = None
    motor_connector: CatalogConnectorRecord = None
    
    # Sized power budget
    power_budget: PowerDistributionBudget = None
    
    # Calculated voltage drops
    main_voltage_drop_v: float = 0.0
    esc_voltage_drop_v: float = 0.0
    motor_voltage_drop_v: float = 0.0
    
    # Calculated power losses
    wiring_power_loss_w: float = 0.0
    connector_power_loss_w: float = 0.0
    regulator_power_loss_w: float = 0.0
    
    # Efficiencies & safety margins
    electrical_efficiency: float = 0.0
    safety_margin_pct: float = 0.0
