"""
ArmGeometry Subsystem

Purpose:
    Defines the `ArmGeometry` domain model representing multirotor arm structural parameters.

Role in Architecture:
    `ArmGeometry` encapsulates arm length in mm, tube outer/inner diameter in mm, motor mounting bolt pattern,
    arm material, and folding mechanism capability.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ArmGeometry:
    """
    Multirotor arm structural geometry definition.

    Attributes:
        arm_length_mm (float): Individual arm tube length from center plate center to motor axis in mm.
        arm_tube_outer_diameter_mm (float): Arm carbon fiber tube outer diameter in mm (e.g. 16mm, 25mm, 30mm).
        arm_tube_inner_diameter_mm (float): Arm carbon fiber tube inner diameter in mm.
        motor_mounting_pattern_mm (str): Motor mounting bolt circle pattern string (e.g. '16x19 / 19x25').
        material (str): Structural arm material description (e.g. 'Carbon Fiber 3K Weave').
        folding_mechanism (bool): True if arm features a folding hinge mechanism.
        metadata (dict[str, Any]): Additional arm diagnostic metadata.
    """

    arm_length_mm: float
    arm_tube_outer_diameter_mm: float = 25.0
    arm_tube_inner_diameter_mm: float = 23.0
    motor_mounting_pattern_mm: str = "16x19 / 19x25"
    material: str = "Carbon Fiber 3K Weave"
    folding_mechanism: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
