"""
Fixed-Wing Tail Requirements Subsystem

Purpose:
    Defines the `TailRequirements` class representing input preferences and operational contexts
    for empennage design.

Role in Architecture:
    `TailRequirements` accepts preceding engineering results (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`)
    and allows user selection or override of the tail configuration layout.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult


class TailConfigType(str, Enum):
    """Supported tail assembly style classifications."""
    CONVENTIONAL = "Conventional"
    T_TAIL = "T-Tail"
    V_TAIL = "V-Tail"
    INVERTED_V_TAIL = "Inverted V-Tail"
    TWIN_TAIL = "Twin Tail"
    TWIN_BOOM = "Twin Boom"
    CANARD = "Canard"
    TAILLESS = "Tailless"
    FLYING_WING = "Flying Wing"
    CUSTOM = "Custom"


@dataclass(slots=True)
class TailRequirements:
    """
    Input model encapsulating preceding engineering results and tail configuration overrides.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        preferred_tail_configuration (TailConfigType | None): Optional user override for tail style.
        metadata (dict[str, Any]): Additional operational overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    preferred_tail_configuration: TailConfigType | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
