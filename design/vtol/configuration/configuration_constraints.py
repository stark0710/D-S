"""
VTOL Configuration Constraints Subsystem

Purpose:
    Defines the `ConfigurationConstraints` class storing architectural limitations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from backend.design.vtol.mission.mission_requirements import VTOLType


@dataclass(slots=True)
class ConfigurationConstraints:
    """
    Limits imposed by safety standards, stability, and structure on layouts.

    Attributes:
        allowed_vtol_types (List[VTOLType]): Allowable VTOL layout architectures.
        min_motor_count (int): Minimum motor count for controllability.
        max_motor_count (int): Maximum motor count due to ESC weight and wiring.
        requires_folding_propellers (bool): Flag indicating lift props must fold.
        max_propeller_diameter_m (float): Maximum physical clearance for props.
        metadata (Dict[str, Any]): Additional operational limits.
    """

    allowed_vtol_types: List[VTOLType]
    min_motor_count: int
    max_motor_count: int
    requires_folding_propellers: bool
    max_propeller_diameter_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
