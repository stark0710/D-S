"""
MissionComplexity Enumeration Subsystem

Purpose:
    Defines the `MissionComplexity` enumeration representing deterministic mission difficulty levels.

Role in Architecture:
    `MissionComplexity` categorizes mission profile difficulty based on payload mass, range, endurance,
    operating environment, and takeoff/landing constraints. It is consumed by the Vehicle Recommendation Engine.
"""

from enum import Enum


class MissionComplexity(str, Enum):
    """
    Mission difficulty complexity level classification.

    Members:
        VERY_LOW: Basic low-altitude, short-range, light payload mission.
        LOW: Standard mission with modest range and payload targets.
        MEDIUM: Moderate payload, multi-kilometer range, or non-standard environment.
        HIGH: Heavy payload, long endurance/range, or severe environmental conditions.
        VERY_HIGH: Extreme payload/endurance, high altitude, or hostile operational environment.
    """
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
