"""
VTOL Authoritative Configuration Model.

Purpose:
    Defines the `VTOLConfiguration` dataclass providing the authoritative definition
    of the physical layout, propulsion arrangement, and structural concept for VTOL aircraft.

Role in Architecture:
    `VTOLConfiguration` serves as the single source of truth for downstream multidisciplinary
    stages (lift system, forward propulsion, wing, tail, fuselage, mass properties, etc.)
    preventing independent assumptions of motor counts, boom counts, or propulsion layouts.
"""

from dataclasses import dataclass, field
from typing import Any, Dict
from backend.design.vtol.mission.mission_requirements import VTOLType


@dataclass(slots=True)
class VTOLConfiguration:
    """
    Authoritative configuration representation for VTOL aircraft.

    For Phase 1, primary support focuses on QuadPlane and Lift + Cruise architectures.
    """

    configuration_type: VTOLType = VTOLType.QUADPLANE
    lift_motor_count: int = 4
    lift_rotor_count: int = 4
    cruise_propulsion_count: int = 1
    propulsion_arrangement: str = "4_lift_plus_1_pusher"
    wing_configuration: str = "High-wing cantilever with twin boom mounts"
    tail_configuration: str = "Inverted V-tail on twin booms"
    landing_configuration: str = "Skids / Skid gear with shock absorbing feet"
    boom_count: int = 2
    rotors_per_boom: int = 2
    has_coaxial_rotors: bool = False
    geometry_metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_quadplane_default(cls, motor_count: int = 4) -> "VTOLConfiguration":
        """Factory creating an authoritative QuadPlane configuration."""
        return cls(
            configuration_type=VTOLType.QUADPLANE,
            lift_motor_count=motor_count,
            lift_rotor_count=motor_count,
            cruise_propulsion_count=1,
            propulsion_arrangement="4_lift_plus_1_pusher",
            wing_configuration="High-wing cantilever with twin boom mounts",
            tail_configuration="Inverted V-tail on twin booms",
            landing_configuration="Skids with carbon fiber reinforcement",
            boom_count=2,
            rotors_per_boom=motor_count // 2,
            has_coaxial_rotors=False,
            geometry_metadata={
                "mount_type": "Composite boom clamp",
                "cruise_thrust_type": "Pusher",
                "surface_control": "Ailerons, Elevator, Rudder",
            },
        )

    @classmethod
    def create_lift_cruise_default(cls, lift_motor_count: int = 4, cruise_motor_count: int = 1) -> "VTOLConfiguration":
        """Factory creating an authoritative Lift + Cruise configuration."""
        return cls(
            configuration_type=VTOLType.LIFT_CRUISE,
            lift_motor_count=lift_motor_count,
            lift_rotor_count=lift_motor_count,
            cruise_propulsion_count=cruise_motor_count,
            propulsion_arrangement=f"{lift_motor_count}_lift_plus_{cruise_motor_count}_cruise",
            wing_configuration="High-wing cantilever with dedicated lift booms",
            tail_configuration="Conventional T-tail or Twin Boom inverted V",
            landing_configuration="Skids / Tricycle landing gear",
            boom_count=2 if lift_motor_count <= 4 else 4,
            rotors_per_boom=lift_motor_count // (2 if lift_motor_count <= 4 else 4),
            has_coaxial_rotors=False,
            geometry_metadata={
                "mount_type": "Dedicated wing boom sleeves",
                "cruise_thrust_type": "Pusher" if cruise_motor_count == 1 else "Twin Wing Nacelles",
                "surface_control": "Full aerodynamic surface control during cruise",
            },
        )
