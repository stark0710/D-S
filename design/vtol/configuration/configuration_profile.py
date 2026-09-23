"""
VTOL Configuration Profile Subsystem

Purpose:
    Defines the `ConfigurationProfile` class summarizing mechanical properties
    of the chosen layout.
"""

from dataclasses import dataclass, field
from typing import Any, Dict
from backend.design.vtol.mission.mission_requirements import VTOLType


@dataclass(slots=True)
class ConfigurationProfile:
    """
    Summary of the physical features of the chosen VTOL layout.

    Attributes:
        vtol_type (VTOLType): VTOL layout classification.
        motor_count (int): Total number of electric motors/engines.
        lift_motor_count (int): Motors used primarily for vertical lift.
        forward_motor_count (int): Motors used primarily for forward propulsion.
        has_wings (bool): Does the configuration have fixed lift surfaces.
        has_tail (bool): Does the configuration have horizontal/vertical tails.
        has_tilt (bool): Does the configuration tilt rotors/wings for transition.
        redundancy_level (str): Level of propulsion fault tolerance.
        metadata (Dict[str, Any]): Detailed architecture choices.
    """

    vtol_type: VTOLType
    motor_count: int
    lift_motor_count: int
    forward_motor_count: int
    has_wings: bool
    has_tail: bool
    has_tilt: bool
    redundancy_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)
