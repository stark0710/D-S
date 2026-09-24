"""
Fixed-Wing Wing Requirements Subsystem

Purpose:
    Defines the `WingRequirements` class representing input preferences and operational contexts
    for sizing fixed-wing lifting surfaces.

Role in Architecture:
    `WingRequirements` accepts the preceding `MissionResult` and `ConfigurationResult` structures,
    optionally combining user layout overrides (e.g. aspect ratio, planform type) to parameterize sizing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult


class PlanformType(str, Enum):
    """Supported wing planform geometry classifications."""
    RECTANGULAR = "Rectangular"
    TAPERED = "Tapered"
    TRAPEZOIDAL = "Trapezoidal"
    ELLIPTICAL = "Elliptical"
    SWEPT = "Swept"
    DELTA = "Delta"
    CRANKED = "Cranked"
    CUSTOM = "Custom"


@dataclass(slots=True)
class WingRequirements:
    """
    Input model encapsulating the mission result, configuration layout, and wing geometry preferences.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        preferred_planform (PlanformType | None): Optional user override for planform geometry.
        preferred_aspect_ratio (float | None): Optional user override for wing Aspect Ratio.
        preferred_wing_loading (float | None): Optional user override for wing loading in kg/m2.
        metadata (dict[str, Any]): Additional operational tags.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    preferred_planform: PlanformType | None = None
    preferred_aspect_ratio: float | None = None
    preferred_wing_loading: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
