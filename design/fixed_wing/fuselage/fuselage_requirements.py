"""
Fixed-Wing Fuselage Requirements Subsystem

Purpose:
    Defines the `FuselageRequirements` class representing input preferences and operational contexts
    for fuselage and packaging design.

Role in Architecture:
    `FuselageRequirements` accepts preceding engineering results (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`)
    and allows user selection or override of the fuselage type.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult


class FuselageType(str, Enum):
    """Supported fuselage layout category classifications."""
    CONVENTIONAL = "Conventional"
    POD_AND_BOOM = "Pod-and-Boom"
    TWIN_BOOM = "Twin Boom"
    FLYING_WING_CENTER = "Flying Wing Center Body"
    BLENDED_BODY = "Blended Body"
    CANARD_FUSELAGE = "Canard Fuselage"
    CUSTOM = "Custom"


@dataclass(slots=True)
class FuselageRequirements:
    """
    Input model encapsulating preceding engineering results and fuselage overrides.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        tail_result (TailResult): Output from tail sizing.
        preferred_fuselage_type (FuselageType | None): Optional user override for fuselage type.
        metadata (dict[str, Any]): Additional operational overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    preferred_fuselage_type: FuselageType | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
