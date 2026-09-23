"""
ValidationCode Enumeration Subsystem

Purpose:
    Defines the `ValidationCode` enumeration representing standardized requirement validation error codes.

Role in Architecture:
    `ValidationCode` provides machine-readable error classification codes attached to `ValidationIssue` objects,
    enabling programmatic handling by user interfaces and diagnostic logging.
"""

from enum import Enum


class ValidationCode(str, Enum):
    """
    Standardized validation code classification.

    Members:
        REQUIRED_FIELD_MISSING: A mandatory field was omitted.
        NEGATIVE_VALUE: A numeric parameter is negative.
        ZERO_VALUE: A numeric parameter is zero where positive non-zero is required.
        INVALID_RANGE: Parameter value falls outside physically achievable bounds.
        INVALID_BUDGET: Specified financial budget is invalid or zero.
        INVALID_PAYLOAD: Specified payload mass is invalid or non-positive.
        INVALID_FLIGHT_TIME: Specified target flight time is invalid or non-positive.
        INVALID_RANGE_REQUIREMENT: Specified target range is invalid or non-positive.
        INVALID_CRUISE_SPEED: Specified cruise speed is invalid or non-positive.
        INVALID_TAKEOFF_WEIGHT: Maximum takeoff weight limit is less than payload weight.
        INVALID_TAKEOFF_LANDING_COMBINATION: Takeoff and landing methods are physically incompatible.
        AIRCRAFT_TYPE_REQUIRED: Aircraft type is mandatory in Manual mode but missing.
        UNSUPPORTED_MISSION_CONFIGURATION: Combination of parameters is unsupported.
        CUSTOM: User-defined custom validation issue.
    """
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    ZERO_VALUE = "ZERO_VALUE"
    INVALID_RANGE = "INVALID_RANGE"
    INVALID_BUDGET = "INVALID_BUDGET"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    INVALID_FLIGHT_TIME = "INVALID_FLIGHT_TIME"
    INVALID_RANGE_REQUIREMENT = "INVALID_RANGE_REQUIREMENT"
    INVALID_CRUISE_SPEED = "INVALID_CRUISE_SPEED"
    INVALID_TAKEOFF_WEIGHT = "INVALID_TAKEOFF_WEIGHT"
    INVALID_TAKEOFF_LANDING_COMBINATION = "INVALID_TAKEOFF_LANDING_COMBINATION"
    AIRCRAFT_TYPE_REQUIRED = "AIRCRAFT_TYPE_REQUIRED"
    UNSUPPORTED_MISSION_CONFIGURATION = "UNSUPPORTED_MISSION_CONFIGURATION"
    CUSTOM = "CUSTOM"
