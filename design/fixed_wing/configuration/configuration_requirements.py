"""
Fixed-Wing Aircraft Configuration Requirements Subsystem

Purpose:
    Defines the input requirements and support enums for selecting the aircraft architecture.

Role in Architecture:
    `ConfigurationRequirements` wraps `MissionResult` and accepts user design overrides
    before determining the optimal configuration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult


class WingPosition(str, Enum):
    """Supported wing mounting positions."""
    HIGH_WING = "High Wing"
    MID_WING = "Mid Wing"
    LOW_WING = "Low Wing"
    PARASOL_WING = "Parasol Wing"
    SHOULDER_WING = "Shoulder Wing"


class PropulsionLayout(str, Enum):
    """Supported propulsion layouts."""
    TRACTOR = "Tractor"
    PUSHER = "Pusher"
    TWIN_TRACTOR = "Twin Tractor"
    TWIN_PUSHER = "Twin Pusher"
    TWIN_BOOM_PUSHER = "Twin Boom Pusher"
    DISTRIBUTED = "Distributed Propulsion"


class TailConfiguration(str, Enum):
    """Supported tail assembly configurations."""
    CONVENTIONAL = "Conventional"
    T_TAIL = "T-Tail"
    V_TAIL = "V-Tail"
    TWIN_BOOM = "Twin Boom"
    TWIN_TAIL = "Twin Tail"
    CANARD = "Canard"
    TAILLESS = "Tailless"
    FLYING_WING = "Flying Wing"


class LandingGearConfiguration(str, Enum):
    """Supported landing gear architectures."""
    TRICYCLE = "Tricycle"
    TAILDRAGGER = "Taildragger"
    BELLY_LANDING = "Belly Landing"
    SKID = "Skid"
    FIXED_GEAR = "Fixed Gear"
    RETRACTABLE = "Retractable"


@dataclass(slots=True)
class ConfigurationRequirements:
    """
    Input model encapsulating the mission context and user preferences for aircraft architecture selection.

    Attributes:
        mission_result (MissionResult): The output of the preceding mission engineering stage.
        preferred_wing_position (WingPosition | None): Optional user override for wing placement.
        preferred_propulsion_layout (PropulsionLayout | None): Optional user override for propulsion location.
        preferred_tail_configuration (TailConfiguration | None): Optional user override for tail style.
        preferred_landing_gear (LandingGearConfiguration | None): Optional user override for landing gear setup.
        metadata (dict[str, Any]): Additional operational tags.
    """

    mission_result: MissionResult
    preferred_wing_position: WingPosition | None = None
    preferred_propulsion_layout: PropulsionLayout | None = None
    preferred_tail_configuration: TailConfiguration | None = None
    preferred_landing_gear: LandingGearConfiguration | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
