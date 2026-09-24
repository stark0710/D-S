"""
MissionType Enumeration Subsystem

Purpose:
    Defines the `MissionType` enumeration representing operational mission classifications for aircraft design.

Role in Architecture:
    `MissionType` serves as a core domain model attribute in `RequirementModel`. It classifies the primary
    intent of the aircraft (e.g. Survey, Mapping, Delivery, Agriculture, Military), influencing mission profile
    calculations in the Mission Analysis Engine and scoring in the Vehicle Recommendation Engine.
"""

from enum import Enum


class MissionType(str, Enum):
    """
    Operational mission type classification for an aircraft design.

    Members:
        SURVEY: Aerial surveying and topographical reconnaissance.
        MAPPING: Photogrammetry and high-resolution 3D mapping.
        DELIVERY: Cargo, medical, or payload transport logistics.
        AGRICULTURE: Crop spraying, health monitoring, and precision farming.
        INSPECTION: Infrastructure, powerline, pipeline, and structural inspection.
        SECURITY: Surveillance, perimeter monitoring, and law enforcement support.
        DISASTER_RESPONSE: Search and rescue, emergency payload drop, and disaster assessment.
        MILITARY: Tactical reconnaissance and defense support operations.
        RESEARCH: Scientific data collection, atmospheric sensing, and testing.
        TRAINING: Flight instruction and pilot skill development.
        CUSTOM: User-defined custom mission profile.
    """
    SURVEY = "SURVEY"
    MAPPING = "MAPPING"
    DELIVERY = "DELIVERY"
    AGRICULTURE = "AGRICULTURE"
    INSPECTION = "INSPECTION"
    SECURITY = "SECURITY"
    DISASTER_RESPONSE = "DISASTER_RESPONSE"
    MILITARY = "MILITARY"
    RESEARCH = "RESEARCH"
    TRAINING = "TRAINING"
    CUSTOM = "CUSTOM"
