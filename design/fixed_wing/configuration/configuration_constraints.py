"""
Fixed-Wing Aircraft Configuration Constraints Subsystem

Purpose:
    Defines the `ConfigurationConstraints` domain model representing constraints on architecture choices.

Role in Architecture:
    `ConfigurationConstraints` defines the bounds of valid aircraft layouts based on payload weight,
    takeoff/landing constraints, and environmental requirements.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.configuration.configuration_requirements import (
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)


@dataclass(slots=True)
class ConfigurationConstraints:
    """
    Limits and constraints restricting the aircraft configuration space.

    Attributes:
        allowed_wing_positions (List[WingPosition]): Permitted wing placements.
        allowed_propulsion_layouts (List[PropulsionLayout]): Permitted motor configurations.
        allowed_tail_configurations (List[TailConfiguration]): Permitted tail configurations.
        allowed_landing_gear_configurations (List[LandingGearConfiguration]): Permitted landing gear configurations.
        min_engines (int): Minimum number of engines allowed.
        max_engines (int): Maximum number of engines allowed.
        runway_required (bool): If true, requires landing/takeoff runways.
        catapult_compatible (bool): If true, compatible with catapult launch.
        hand_launch_compatible (bool): If true, compatible with hand launch.
    """

    allowed_wing_positions: List[WingPosition] = field(default_factory=list)
    allowed_propulsion_layouts: List[PropulsionLayout] = field(default_factory=list)
    allowed_tail_configurations: List[TailConfiguration] = field(default_factory=list)
    allowed_landing_gear_configurations: List[LandingGearConfiguration] = field(default_factory=list)
    min_engines: int = 1
    max_engines: int = 2
    runway_required: bool = False
    catapult_compatible: bool = True
    hand_launch_compatible: bool = True
