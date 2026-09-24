"""
Fixed-Wing Payload Sizing Constraints Subsystem

Purpose:
    Defines the `PayloadConstraints` class to hold physical bounds.

Role in Architecture:
    `PayloadConstraints` collects weight limits, power limits, and allowed payload types.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.payload.payload_requirements import PayloadType


@dataclass(slots=True)
class PayloadConstraints:
    """
    Sizing bounds restricting weight, power, and bandwidth of the integrated payload.

    Attributes:
        allowed_types (List[PayloadType]): Approved payload categories.
        max_payload_weight_kg (float): Sized max load capability from mission profile.
        max_payload_power_w (float): Sized limit on continuous electrical load.
        max_bandwidth_mbps (float): Sized telemetry link capacity limits.
    """

    allowed_types: List[PayloadType] = field(default_factory=list)
    max_payload_weight_kg: float = 2.0
    max_payload_power_w: float = 20.0
    max_bandwidth_mbps: float = 10.0
