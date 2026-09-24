"""
Pipeline Result and Aircraft Specification Models for VTOL Design Execution.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.fuselage.fuselage_result import FuselageResult
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult
from backend.design.vtol.electrical.electrical_result import ElectricalResult
from backend.design.vtol.avionics.avionics_result import AvionicsResult
from backend.design.vtol.payload.payload_result import PayloadResult
from backend.design.vtol.mass_properties.mass_result import MassResult
from backend.design.vtol.hover_performance.hover_result import HoverResult
from backend.design.vtol.transition.transition_result import TransitionResult
from backend.design.vtol.cruise_performance.cruise_result import CruiseResult
from backend.design.vtol.verification.verification_result import VerificationResult
from backend.design.vtol.cad.cad_result import CADResult
from backend.design.vtol.manufacturing.manufacturing_result import ManufacturingResult
from backend.design.vtol.report.report_result import ReportResult

from backend.design.vtol.pipeline.convergence import IterationRecord


import math
import dataclasses

class PipelineStatus(str, Enum):
    """Execution status codes for VTOL Design Pipeline."""
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    FAILED = "FAILED"
    INVALID_REQUIREMENTS = "INVALID_REQUIREMENTS"
    CONFIGURATION_INFEASIBLE = "CONFIGURATION_INFEASIBLE"
    SIZING_INFEASIBLE = "SIZING_INFEASIBLE"
    CONVERGENCE_FAILED = "CONVERGENCE_FAILED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    
    # Phase 5B / Sizing error categories
    AIRFOIL_STRUCTURE_INCOMPATIBLE = "AIRFOIL_STRUCTURE_INCOMPATIBLE"
    PAYLOAD_INFEASIBLE = "PAYLOAD_INFEASIBLE"
    PROPULSION_INFEASIBLE = "PROPULSION_INFEASIBLE"
    BATTERY_INFEASIBLE = "BATTERY_INFEASIBLE"
    COMMUNICATION_INFEASIBLE = "COMMUNICATION_INFEASIBLE"
    COMPONENT_DATABASE_LIMITATION = "COMPONENT_DATABASE_LIMITATION"
    MTOW_LIMIT_EXCEEDED = "MTOW_LIMIT_EXCEEDED"
    STABILITY_INFEASIBLE = "STABILITY_INFEASIBLE"
    PERFORMANCE_INFEASIBLE = "PERFORMANCE_INFEASIBLE"
    INTERNAL_EXCEPTION = "INTERNAL_EXCEPTION"


def to_dict_recursive(obj: Any, seen: Optional[set] = None) -> Any:
    """
    Recursively serializes dataclasses, enums, objects, dicts, and lists into JSON-compatible types.
    Prevents cycles, handles inf/nan floats, and avoids returning empty dicts for structured objects.
    """
    if seen is None:
        seen = set()

    if obj is None:
        return None
    if isinstance(obj, (int, str, bool)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, Enum):
        return obj.value

    obj_id = id(obj)
    if obj_id in seen:
        return None
    seen.add(obj_id)

    if dataclasses.is_dataclass(obj):
        res = {}
        for f in dataclasses.fields(obj):
            try:
                val = getattr(obj, f.name, None)
                res[f.name] = to_dict_recursive(val, seen)
            except Exception:
                res[f.name] = None
        return res

    if hasattr(obj, "__slots__"):
        res = {}
        all_slots = set()
        for cls in obj.__class__.__mro__:
            for s in getattr(cls, "__slots__", ()):
                all_slots.add(s)
        for s in all_slots:
            if not s.startswith("_"):
                try:
                    res[s] = to_dict_recursive(getattr(obj, s), seen)
                except Exception:
                    pass
        return res

    if isinstance(obj, dict):
        return {str(k): to_dict_recursive(v, seen) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_dict_recursive(x, seen) for x in obj]

    if hasattr(obj, "__dict__"):
        res = {}
        for k, v in obj.__dict__.items():
            if not k.startswith("_"):
                res[k] = to_dict_recursive(v, seen)
        return res

    return str(obj)


@dataclass
class VTOLAircraftSpecification:
    """
    Comprehensive specification containing all design and analysis results for the VTOL.
    """
    # High-level outputs
    mtow_kg: float = 0.0
    empty_weight_kg: float = 0.0
    payload_weight_kg: float = 0.0
    estimated_endurance_min: float = 0.0
    estimated_range_km: float = 0.0
    configuration_type: str = ""

    # Subsystem Sizing Results
    mission: Optional[MissionResult] = None
    configuration: Optional[ConfigurationResult] = None
    wing: Optional[WingResult] = None
    airfoil: Optional[AirfoilResult] = None
    tail: Optional[TailResult] = None
    fuselage: Optional[FuselageResult] = None
    lift_system: Optional[LiftSystemResult] = None
    forward_propulsion: Optional[ForwardPropulsionResult] = None
    electrical: Optional[ElectricalResult] = None
    avionics: Optional[AvionicsResult] = None
    payload: Optional[PayloadResult] = None
    mass_properties: Optional[MassResult] = None
    hover_performance: Optional[HoverResult] = None
    transition: Optional[TransitionResult] = None
    cruise_performance: Optional[CruiseResult] = None
    
    # Validation, CAD, and manufacturing outputs
    verification: Optional[VerificationResult] = None
    cad: Optional[CADResult] = None
    manufacturing: Optional[ManufacturingResult] = None
    report: Optional[ReportResult] = None

    # Phase 1 Foundation additions
    vtol_configuration: Optional[Any] = None
    fixed_wing_subsystems: Optional[Any] = None
    stage_statuses: Dict[str, str] = field(default_factory=dict)


@dataclass
class VTOLDesignResult:
    """
    Consolidated response payload from the VTOL design synthesis orchestrator.
    """
    success: bool
    status: PipelineStatus
    iterations: int
    converged: bool

    convergence_history: List[IterationRecord] = field(default_factory=list)
    final_specification: Optional[VTOLAircraftSpecification] = None
    requirements: Optional[Any] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.success and self.status == PipelineStatus.SUCCESS

    @property
    def specification(self) -> Optional[VTOLAircraftSpecification]:
        return self.final_specification

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result recursively to JSON-compatible dict."""
        return to_dict_recursive(self)
