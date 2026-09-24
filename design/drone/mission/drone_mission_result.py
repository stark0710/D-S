"""
DroneMissionResult Subsystem

Purpose:
    Defines the `DroneMissionResult` domain model representing output from the Drone Mission Engineering Framework.

Role in Architecture:
    `DroneMissionResult` encapsulates the `DroneMissionProfile`, derived `DroneMissionRequirements`,
    `DroneMissionConstraints`, warnings list, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.mission.drone_mission_requirements import DroneMissionRequirements
from backend.design.drone.mission.drone_mission_constraints import DroneMissionConstraints


@dataclass(slots=True)
class DroneMissionResult:
    """
    Multirotor mission engineering output summary.

    Attributes:
        mission_profile (DroneMissionProfile): Input multirotor mission profile.
        engineering_requirements (DroneMissionRequirements): Derived multirotor engineering requirements.
        constraints (DroneMissionConstraints): Derived physical & operational constraints.
        warnings (list[str]): Diagnostic warnings generated during mission decomposition.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    mission_profile: DroneMissionProfile
    engineering_requirements: DroneMissionRequirements
    constraints: DroneMissionConstraints
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
