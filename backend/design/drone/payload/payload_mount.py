"""
PayloadMount Subsystem

Purpose:
    Defines the `PayloadMount` domain model representing physical payload mounting and mechanical integration.

Role in Architecture:
    `PayloadMount` specifies mounting mechanism type ('QUICK_RELEASE_RAIL', 'BOTTOM_PLATE_BOLTS', 'GIMBAL_DAMPED'),
    vibration isolation damping, quick-release locking, mounting location, max mass rating, and mount mass.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadMount:
    """
    Multirotor payload mounting mechanical integration specification model.

    Attributes:
        mount_type (str): Mounting mechanism classification.
        vibration_dampers (bool): True if anti-vibration silicone dampeners are integrated.
        quick_release (bool): True if tool-less quick release mechanism is included.
        location (str): Physical mounting location ('BOTTOM_CENTER', 'FRONT_NOSE', 'UNDER_BELLY').
        max_supported_mass_kg (float): Maximum payload mass rating in kg.
        weight_g (float): Mass of mount mechanism in grams.
        metadata (dict[str, Any]): Additional mount metadata.
    """

    mount_type: str = "QUICK_RELEASE_RAIL"
    vibration_dampers: bool = True
    quick_release: bool = True
    location: str = "BOTTOM_CENTER"
    max_supported_mass_kg: float = 10.0
    weight_g: float = 120.0
    metadata: dict[str, Any] = field(default_factory=dict)
