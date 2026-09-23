"""
RecommendationReason Enumeration Subsystem

Purpose:
    Defines the `RecommendationReason` enumeration representing specific criteria driving category recommendations.

Role in Architecture:
    `RecommendationReason` classifies the engineering drivers (e.g. Payload Capability, Hover Capability, Range, Cruise Efficiency)
    behind suitability scores and trade-off findings.
"""

from enum import Enum


class RecommendationReason(str, Enum):
    """
    Standardized engineering recommendation criteria tags.

    Members:
        PAYLOAD_CAPABILITY: Payload mass capacity vs structural fraction.
        FLIGHT_TIME: Endurance / flight time capability.
        RANGE: Distance coverage capability.
        CRUISE_EFFICIENCY: Aerodynamic lift-to-drag cruise efficiency.
        HOVER_CAPABILITY: Stationary hover and low-speed maneuvering capability.
        VERTICAL_TAKEOFF: Precision vertical takeoff capability without runways.
        RUNWAY_REQUIREMENT: Requirement for ground roll takeoff/landing runways.
        MISSION_COMPLEXITY: Suitability relative to assessed mission complexity.
        OPERATING_ENVIRONMENT: Robustness in target terrain/weather environment.
        BUDGET: Financial component and manufacturing cost alignment.
        COST_EFFICIENCY: Operating cost per kilometer/hour.
        MAINTENANCE_COMPLEXITY: Mechanical complexity and field serviceability.
        MANUFACTURING_COMPLEXITY: Airframe fabrication difficulty.
        FUTURE_SCALABILITY: Growth potential for future payload or battery upgrades.
    """
    PAYLOAD_CAPABILITY = "PAYLOAD_CAPABILITY"
    FLIGHT_TIME = "FLIGHT_TIME"
    RANGE = "RANGE"
    CRUISE_EFFICIENCY = "CRUISE_EFFICIENCY"
    HOVER_CAPABILITY = "HOVER_CAPABILITY"
    VERTICAL_TAKEOFF = "VERTICAL_TAKEOFF"
    RUNWAY_REQUIREMENT = "RUNWAY_REQUIREMENT"
    MISSION_COMPLEXITY = "MISSION_COMPLEXITY"
    OPERATING_ENVIRONMENT = "OPERATING_ENVIRONMENT"
    BUDGET = "BUDGET"
    COST_EFFICIENCY = "COST_EFFICIENCY"
    MAINTENANCE_COMPLEXITY = "MAINTENANCE_COMPLEXITY"
    MANUFACTURING_COMPLEXITY = "MANUFACTURING_COMPLEXITY"
    FUTURE_SCALABILITY = "FUTURE_SCALABILITY"
