"""
VTOL Configuration Requirements Subsystem

Purpose:
    Defines the `ConfigurationRequirements` class capturing layout design desires
    and packaging parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.mission.mission_requirements import VTOLType


@dataclass(slots=True)
class ConfigurationRequirements:
    """
    Inputs for VTOL configuration sizing.

    Attributes:
        mission_result (MissionResult): The result from the mission engineering stage.
        preferred_vtol_type (VTOLType | None): Preferred vehicle layout override.
        desired_motor_count (int | None): Optional specific motor count override.
        redundancy_requirement (str): Desired fault tolerance level (e.g., None, Quad-fault, Octo-redundant).
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    preferred_vtol_type: VTOLType | None = None
    desired_motor_count: int | None = None
    redundancy_requirement: str = "None"
    metadata: Dict[str, Any] = field(default_factory=dict)
