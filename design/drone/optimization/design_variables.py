"""
DesignVariables Subsystem

Purpose:
    Defines the `DesignVariables` domain model representing multirotor optimization variables.

Role in Architecture:
    `DesignVariables` specifies adjustable frame size, motor size/KV, propeller size/pitch, battery capacity/S-count,
    ESC rating, payload placement, battery placement, and landing gear options for candidate design search space.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DesignVariables:
    """
    Multirotor design variables vector model.

    Attributes:
        wheelbase_mm (float): Adjustable frame wheelbase in mm.
        motor_kv (int): Adjustable motor KV rating.
        propeller_diameter_inch (float): Adjustable propeller diameter in inches.
        battery_capacity_mah (float): Adjustable battery capacity in mAh.
        battery_cell_count_s (int): Adjustable battery S-count (4S, 6S, 12S).
        esc_current_rating_a (float): Adjustable ESC current rating in A.
        battery_offset_z_mm (float): Adjustable vertical/longitudinal battery placement offset in mm.
        metadata (dict[str, Any]): Additional design variables metadata.
    """

    wheelbase_mm: float = 680.0
    motor_kv: int = 400
    propeller_diameter_inch: float = 13.0
    battery_capacity_mah: float = 10000.0
    battery_cell_count_s: int = 6
    esc_current_rating_a: float = 50.0
    battery_offset_z_mm: float = -40.0
    metadata: dict[str, Any] = field(default_factory=dict)
