"""
ScoreCategory Enumeration Subsystem

Purpose:
    Defines the `ScoreCategory` enumeration representing quantitative engineering scoring categories.

Role in Architecture:
    `ScoreCategory` classifies performance parameters evaluated by the Universal Engineering Scoring Framework.
"""

from enum import Enum


class ScoreCategory(str, Enum):
    """
    Engineering scoring category classification.

    Members:
        PAYLOAD: Payload capacity and mass fraction performance.
        ENDURANCE: Flight time endurance capability.
        RANGE: Operational range distance capability.
        CRUISE_SPEED: Cruise speed and dash speed capability.
        EFFICIENCY: Energy consumption (Wh/km or Lift/Drag ratio) efficiency.
        POWER_MARGIN: Motor and ESC electrical power margin.
        WEIGHT: Structural mass margin relative to MTOW limit.
        COST: Financial cost efficiency relative to budget.
        RELIABILITY: System component redundancy and MTBF reliability.
        MAINTAINABILITY: Ease of field servicing and maintenance.
        MANUFACTURABILITY: Airframe fabrication ease.
        SAFETY: Flight control safety margin and thrust redundancy.
        EXPANDABILITY: Upgrade headroom for future payloads/batteries.
        MISSION_FITNESS: Overall mission objective suitability score.
    """
    PAYLOAD = "PAYLOAD"
    ENDURANCE = "ENDURANCE"
    RANGE = "RANGE"
    CRUISE_SPEED = "CRUISE_SPEED"
    EFFICIENCY = "EFFICIENCY"
    POWER_MARGIN = "POWER_MARGIN"
    WEIGHT = "WEIGHT"
    COST = "COST"
    RELIABILITY = "RELIABILITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    MANUFACTURABILITY = "MANUFACTURABILITY"
    SAFETY = "SAFETY"
    EXPANDABILITY = "EXPANDABILITY"
    MISSION_FITNESS = "MISSION_FITNESS"
