"""
MassModel Subsystem

Purpose:
    Defines the `MassModel` domain model representing overall aircraft mass properties parameters.

Role in Architecture:
    `MassModel` encapsulates total mass in kg, empty mass in kg, payload mass in kg, and 3D CG position.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.center_of_gravity import CenterOfGravity


@dataclass(slots=True)
class MassModel:
    """
    Multirotor overall aircraft mass model definition.

    Attributes:
        total_mass_kg (float): Total All-Up Weight (AUW) in kg.
        empty_mass_kg (float): Bare empty aircraft mass (without payload/battery) in kg.
        payload_mass_kg (float): Payload mass in kg.
        center_of_gravity (CenterOfGravity): 3D CG model.
        metadata (dict[str, Any]): Additional mass model metadata.
    """

    total_mass_kg: float
    empty_mass_kg: float
    payload_mass_kg: float
    center_of_gravity: CenterOfGravity
    metadata: dict[str, Any] = field(default_factory=dict)
