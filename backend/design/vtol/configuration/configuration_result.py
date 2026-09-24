"""
VTOL Configuration Result Subsystem

Purpose:
    Defines the consolidated `ConfigurationResult` dataclass outputted by this stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.configuration.propulsion_layout import PropulsionLayout
from backend.design.vtol.configuration.flight_mode_configuration import FlightModeConfiguration
from backend.design.vtol.configuration.actuator_layout import ActuatorLayout
from backend.design.vtol.configuration.configuration_analysis import ConfigurationAnalysis


from backend.design.vtol.configuration.vtol_configuration import VTOLConfiguration


@dataclass(slots=True)
class ConfigurationResult:
    """
    Consolidated configuration output package detailing chosen mechanical layout
    and flight control allocations.

    Attributes:
        selected_configuration (VTOLType): The mechanical layout type selected.
        lift_architecture (PropulsionLayout): Vertical thrust setup.
        forward_propulsion_layout (PropulsionLayout): Forward thrust setup.
        flight_mode_configuration (FlightModeConfiguration): configured flight modes.
        actuator_layout (ActuatorLayout): Servo and motor channel layouts.
        configuration_analysis (ConfigurationAnalysis): Evaluation trade-offs.
        vtol_configuration (VTOLConfiguration | None): Authoritative VTOL layout definition.
        engineering_notes (List[str]): Sizing layout observations.
        recommendations (List[str]): Engineering recommendations.
        warnings (List[str]): Configuration compliance warnings.
        metadata (Dict[str, Any]): execution timestamps and versions.
    """

    selected_configuration: VTOLType
    lift_architecture: PropulsionLayout
    forward_propulsion_layout: PropulsionLayout
    flight_mode_configuration: FlightModeConfiguration
    actuator_layout: ActuatorLayout
    configuration_analysis: ConfigurationAnalysis
    vtol_configuration: Optional[VTOLConfiguration] = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
