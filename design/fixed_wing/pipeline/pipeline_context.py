"""
Pipeline Context Container for Fixed-Wing Design Sizing.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from backend.design.common.requirements.requirement_model import RequirementModel

@dataclass
class FixedWingPipelineContext:
    """
    Internal state container carrying execution context across pipeline stages.
    """
    # Sprint 33 requested fields
    mission_requirements: Optional[RequirementModel] = None
    current_design_state: Dict[str, Any] = field(default_factory=dict)
    subsystem_specifications: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    certification_status: Optional[str] = None
    certification_report: Optional[Any] = None

    # Backward compatibility fields
    requirements: Optional[RequirementModel] = None
    current_mtow: float = 0.0
    previous_mtow: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.requirements is None:
            self.requirements = self.mission_requirements
        if self.mission_requirements is None:
            self.mission_requirements = self.requirements
        if "errors" not in self.diagnostics:
            self.diagnostics["errors"] = self.errors
        if "warnings" not in self.diagnostics:
            self.diagnostics["warnings"] = self.warnings

    # Properties to dynamically map backward compatibility fields if needed
    @property
    def mission_result(self) -> Any:
        return self.current_design_state.get("mission_result")

    @mission_result.setter
    def mission_result(self, value: Any) -> None:
        self.current_design_state["mission_result"] = value

    @property
    def configuration_result(self) -> Any:
        return self.current_design_state.get("configuration_result")

    @configuration_result.setter
    def configuration_result(self, value: Any) -> None:
        self.current_design_state["configuration_result"] = value

    @property
    def construction_result(self) -> Any:
        return self.current_design_state.get("construction_result")

    @construction_result.setter
    def construction_result(self, value: Any) -> None:
        self.current_design_state["construction_result"] = value

    @property
    def wing_result(self) -> Any:
        return self.current_design_state.get("wing_result")

    @wing_result.setter
    def wing_result(self, value: Any) -> None:
        self.current_design_state["wing_result"] = value

    @property
    def airfoil_result(self) -> Any:
        return self.current_design_state.get("airfoil_result")

    @airfoil_result.setter
    def airfoil_result(self, value: Any) -> None:
        self.current_design_state["airfoil_result"] = value

    @property
    def tail_result(self) -> Any:
        return self.current_design_state.get("tail_result")

    @tail_result.setter
    def tail_result(self, value: Any) -> None:
        self.current_design_state["tail_result"] = value

    @property
    def fuselage_result(self) -> Any:
        return self.current_design_state.get("fuselage_result")

    @fuselage_result.setter
    def fuselage_result(self, value: Any) -> None:
        self.current_design_state["fuselage_result"] = value

    @property
    def propulsion_result(self) -> Any:
        return self.current_design_state.get("propulsion_result")

    @propulsion_result.setter
    def propulsion_result(self, value: Any) -> None:
        self.current_design_state["propulsion_result"] = value

    @property
    def electrical_result(self) -> Any:
        return self.current_design_state.get("electrical_result")

    @electrical_result.setter
    def electrical_result(self, value: Any) -> None:
        self.current_design_state["electrical_result"] = value

    @property
    def avionics_result(self) -> Any:
        return self.current_design_state.get("avionics_result")

    @avionics_result.setter
    def avionics_result(self, value: Any) -> None:
        self.current_design_state["avionics_result"] = value

    @property
    def payload_result(self) -> Any:
        return self.current_design_state.get("payload_result")

    @payload_result.setter
    def payload_result(self, value: Any) -> None:
        self.current_design_state["payload_result"] = value

    @property
    def mass_properties_result(self) -> Any:
        return self.current_design_state.get("mass_properties_result")

    @mass_properties_result.setter
    def mass_properties_result(self, value: Any) -> None:
        self.current_design_state["mass_properties_result"] = value

    @property
    def performance_result(self) -> Any:
        return self.current_design_state.get("performance_result")

    @performance_result.setter
    def performance_result(self, value: Any) -> None:
        self.current_design_state["performance_result"] = value

    @property
    def verification_result(self) -> Any:
        return self.current_design_state.get("verification_result")

    @verification_result.setter
    def verification_result(self, value: Any) -> None:
        self.current_design_state["verification_result"] = value
