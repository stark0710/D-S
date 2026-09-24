from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.battery.battery_result import BatterySpecification, PropulsionAssembly
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.layout.layout_result import LayoutSpecification
from backend.design.multirotor.mass_properties.mass_result import MassPropertiesSpecification
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.common.verification.certification_report import AircraftCertificationReport


class PipelineStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_REQUIREMENTS = "INVALID_REQUIREMENTS"
    CONFIGURATION_INFEASIBLE = "CONFIGURATION_INFEASIBLE"
    FRAME_INFEASIBLE = "FRAME_INFEASIBLE"
    PROPULSION_INFEASIBLE = "PROPULSION_INFEASIBLE"
    ELECTRICAL_INFEASIBLE = "ELECTRICAL_INFEASIBLE"
    LAYOUT_INFEASIBLE = "LAYOUT_INFEASIBLE"
    MASS_INFEASIBLE = "MASS_INFEASIBLE"
    PERFORMANCE_INFEASIBLE = "PERFORMANCE_INFEASIBLE"
    CONVERGENCE_FAILED = "CONVERGENCE_FAILED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    DATABASE_LIMITATION = "DATABASE_LIMITATION"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class MultirotorAircraftSpecification:
    """
    Consolidated final aircraft design specification for a multirotor UAV.
    """
    mission_strategy: MissionStrategySpecification
    frame: FrameSpecification
    propulsion_assembly: PropulsionAssembly
    electrical: ElectricalSpecification
    layout_spec: LayoutSpecification
    mass_properties: MassPropertiesSpecification
    performance: PerformanceResult
    verification: AircraftCertificationReport
    convergence_history: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    bom_data: List[Dict[str, Any]] = field(default_factory=list)
    build_instructions: str = ""
    
    @property
    def layout(self) -> str:
        return self.frame.configuration

    
    # Expose fields as properties for verification compliance checks
    @property
    def layout_class(self) -> str:
        return self.frame.configuration

    @property
    def mtow_kg(self) -> float:
        return self.mass_properties.total_mass_kg

    @property
    def empty_weight_kg(self) -> float:
        return self.mass_properties.empty_mass_kg


@dataclass
class MultirotorDesignResult:
    """
    Sizing and optimization outcome returned by MultirotorDesignPipeline.
    """
    success: bool
    status: PipelineStatus
    iterations: int
    converged: bool
    final_specification: Optional[MultirotorAircraftSpecification] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
