"""
ManufacturingRequirements Subsystem

Purpose:
    Defines the `ManufacturingRequirements` domain model representing input requirements for manufacturing engineering.

Role in Architecture:
    `ManufacturingRequirements` specifies target lead time in days, target assembly labor time in hours, and fabrication strategy selection.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ManufacturingRequirements:
    """
    Multirotor manufacturing engineering requirements model.

    Attributes:
        max_lead_time_days (int): Sourcing lead time limit.
        max_assembly_hours (float): Maximum assembly labor hours allowed.
        required_certifications (list[str]): Compliance certifications list (e.g. CE, FCC, ISO9001).
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    max_lead_time_days: int = 15
    max_assembly_hours: float = 12.0
    required_certifications: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
