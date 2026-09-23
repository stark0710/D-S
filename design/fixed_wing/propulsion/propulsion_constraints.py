"""
Fixed-Wing Propulsion Sizing Constraints Subsystem

Purpose:
    Defines the `PropulsionConstraints` class to hold physical bounds.

Role in Architecture:
    `PropulsionConstraints` collects permitted layout boundaries, maximum propeller diameters,
    and thrust-to-weight minimums.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionType


@dataclass(slots=True)
class PropulsionConstraints:
    """
    Sizing bounds restricting motor selection, propeller diameters, and thrust ratios.

    Attributes:
        allowed_types (List[PropulsionType]): Permitted motor styles (Electric, ICE).
        max_prop_diameter_m (float | None): Limit on propeller width due to ground clearance.
        min_thrust_to_weight (float): Minimum thrust-to-weight ratio.
        max_motor_power_w (float | None): Limit on electrical energy draw.
    """

    allowed_types: List[PropulsionType] = field(default_factory=list)
    max_prop_diameter_m: float | None = None
    min_thrust_to_weight: float = 0.45
    max_motor_power_w: float | None = None
