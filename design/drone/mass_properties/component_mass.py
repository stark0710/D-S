"""
ComponentMass Subsystem

Purpose:
    Defines the `ComponentMass` domain model representing an individual component's mass and 3D spatial position.

Role in Architecture:
    `ComponentMass` encapsulates component name, category classification ('STRUCTURE', 'PROPULSION', 'ELECTRICAL', 'AVIONICS', 'PAYLOAD', 'LANDING_GEAR', 'FASTENERS', 'MARGIN'),
    mass in grams, and 3D coordinates (X, Y, Z in mm) relative to frame geometric origin.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ComponentMass:
    """
    Individual component mass and 3D spatial coordinate model.

    Attributes:
        name (str): Component identifier.
        category (str): Subsystem category ('STRUCTURE', 'PROPULSION', 'ELECTRICAL', 'AVIONICS', 'PAYLOAD', 'LANDING_GEAR', 'FASTENERS', 'MARGIN').
        mass_g (float): Component mass in grams.
        position_x_mm (float): X-axis longitudinal coordinate in mm (front + / back -).
        position_y_mm (float): Y-axis lateral coordinate in mm (right + / left -).
        position_z_mm (float): Z-axis vertical coordinate in mm (up + / down -).
        metadata (dict[str, Any]): Additional component metadata.
    """

    name: str
    category: str
    mass_g: float
    position_x_mm: float = 0.0
    position_y_mm: float = 0.0
    position_z_mm: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
