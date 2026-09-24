"""
VTOL Propulsion Layout Subsystem

Purpose:
    Defines the `PropulsionLayout` dataclass detailing the lift and cruise
    propulsion architecture.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class PropulsionLayout:
    """
    Detailed mechanical layout of the VTOL thrust system.

    Attributes:
        lift_system_type (str): Type of vertical lift (e.g., QuadRotor, OctaCoaxial, TiltRotor).
        forward_propulsion_layout (str): Cruise thrust layout (e.g., Pusher, Tractor, Vectored, TailSitter).
        motor_count (int): Total count of electric motors/engines.
        propeller_count (int): Total count of aerodynamic propellers.
        has_pitch_control (bool): True if propellers have variable pitch.
        is_hybrid (bool): True if using internal combustion for range extension.
        mounting_structure (str): Description of mounting structure (e.g., Wing Booms, Nose Mount).
        metadata (Dict[str, Any]): Additional layout details.
    """

    lift_system_type: str
    forward_propulsion_layout: str
    motor_count: int
    propeller_count: int
    has_pitch_control: bool
    is_hybrid: bool
    mounting_structure: str
    metadata: Dict[str, Any] = field(default_factory=dict)
