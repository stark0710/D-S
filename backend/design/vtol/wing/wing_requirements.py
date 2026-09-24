"""
VTOL Wing Requirements Subsystem

Purpose:
    Defines the `WingRequirements` class capturing layout design overrides
    and packaging parameters for the wing stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult


@dataclass(slots=True)
class WingRequirements:
    """
    Inputs for VTOL wing sizing and integration.

    Attributes:
        mission_result (MissionResult): The result from the mission engineering stage.
        configuration_result (ConfigurationResult): The result from the configuration engineering stage.
        preferred_wing_type (str | None): Preferred wing layout override (e.g. High Wing, Box Wing).
        preferred_aspect_ratio (float | None): Preferred aspect ratio override.
        preferred_wing_span_m (float | None): Preferred wingspan override.
        metadata (Dict[str, Any]): Additional override parameters or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    preferred_wing_type: str | None = None
    preferred_aspect_ratio: float | None = None
    preferred_wing_span_m: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
