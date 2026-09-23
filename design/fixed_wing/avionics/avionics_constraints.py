"""
Fixed-Wing Avionics Sizing Constraints Subsystem

Purpose:
    Defines the `AvionicsConstraints` class to hold physical bounds.

Role in Architecture:
    `AvionicsConstraints` collects target communication range limits, allowed controllers,
    and flight controller weight restrictions.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class AvionicsConstraints:
    """
    Sizing bounds restricting avionics, data links, and computers.

    Attributes:
        allowed_controllers (List[str]): Approved flight controller models.
        min_comms_range_km (float): Minimum communication range.
        required_gnss_count (int): Sized GNSS redundancy count.
        max_avionics_weight_g (float | None): Limit on autopilot package weight.
    """

    allowed_controllers: List[str] = field(default_factory=list)
    min_comms_range_km: float = 5.0
    required_gnss_count: int = 1
    max_avionics_weight_g: float | None = None
