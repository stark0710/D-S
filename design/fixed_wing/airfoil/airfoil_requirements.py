"""
Fixed-Wing Airfoil Requirements Subsystem

Purpose:
    Defines the `AirfoilRequirements` class representing input preferences and operational contexts
    for choosing and validating wing airfoils.

Role in Architecture:
    `AirfoilRequirements` wraps the outputs of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`)
    and allows user selection or override of root and tip airfoils.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult


class AirfoilType(str, Enum):
    """Supported airfoil aerodynamic category classifications."""
    SYMMETRICAL = "Symmetrical"
    SEMI_SYMMETRICAL = "Semi-Symmetrical"
    CAMBERED = "Cambered"
    HIGH_LIFT = "High-Lift"
    LAMINAR_FLOW = "Laminar Flow"
    REFLEXED = "Reflexed"
    CUSTOM = "Custom Airfoil"


@dataclass(slots=True)
class AirfoilRequirements:
    """
    Input model encapsulating preceding engineering results and airfoil preferences.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        preferred_root_airfoil (str | None): Optional name of preferred root airfoil.
        preferred_tip_airfoil (str | None): Optional name of preferred tip airfoil.
        metadata (dict[str, Any]): Additional operational overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    preferred_root_airfoil: str | None = None
    preferred_tip_airfoil: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
