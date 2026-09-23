"""
PayloadRequirements Subsystem

Purpose:
    Defines the `PayloadRequirements` domain model representing input requirements for payload engineering.

Role in Architecture:
    `PayloadRequirements` specifies payload type, max payload mass in kg, quick release requirement,
    and gimbal stabilization requirement.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadRequirements:
    """
    Multirotor payload engineering requirements model.

    Attributes:
        payload_type (str): Mission payload type classification.
        max_payload_mass_kg (float): Maximum payload mass capacity in kg.
        quick_release_required (bool): True if tool-less quick-release mechanism is required.
        gimbal_stabilization_required (bool): True if 3-axis active gimbal stabilization is required.
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    payload_type: str = "RGB_CAMERA"
    max_payload_mass_kg: float = 2.0
    quick_release_required: bool = True
    gimbal_stabilization_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
