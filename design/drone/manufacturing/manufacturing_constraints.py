"""
ManufacturingConstraints Subsystem

Purpose:
    Defines the `ManufacturingConstraints` domain model representing production limits.

Role in Architecture:
    `ManufacturingConstraints` specifies upper cost limit in USD, facility capability limits, and material availability parameters.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ManufacturingConstraints:
    """
    Multirotor manufacturing constraints model.

    Attributes:
        max_cost_usd (float): Sourcing cost limit boundary in USD.
        allowed_materials (list[str]): Approved material catalog strings.
        facility_capabilities (list[str]): Facility tooling capabilities list (e.g. 'CNC_3_AXIS', '3D_PRINTER_FDM').
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_cost_usd: float = 3000.0
    allowed_materials: list[str] = field(default_factory=lambda: ["Carbon Fiber", "Aluminum 6061", "PLA", "PETG"])
    facility_capabilities: list[str] = field(default_factory=lambda: ["CNC_3_AXIS", "3D_PRINTER_FDM", "LASER_CUTTER"])
    metadata: dict[str, Any] = field(default_factory=dict)
