"""
AssemblyPlan Subsystem

Purpose:
    Defines the `AssemblyPlan` domain model representing aircraft assembly guidelines.

Role in Architecture:
    `AssemblyPlan` specifies torque specifications, required assembly tools list, and general guidelines.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AssemblyPlan:
    """
    Multirotor assembly guidelines model.

    Attributes:
        required_tools (list[str]): Required assembly tools list.
        torque_specs_n_m (dict[str, float]): Torque limits dictionary in N*m.
        general_precautions (list[str]): Critical assembly precautions list.
        estimated_assembly_time_hours (float): Estimated assembly time in hours.
        metadata (dict[str, Any]): Additional assembly metadata.
    """

    required_tools: list[str] = field(default_factory=list)
    torque_specs_n_m: dict[str, float] = field(default_factory=dict)
    general_precautions: list[str] = field(default_factory=list)
    estimated_assembly_time_hours: float = 4.0
    metadata: dict[str, Any] = field(default_factory=dict)
