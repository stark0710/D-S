from typing import List, Union
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

class MissionValidationError(ValueError):
    """Custom exception raised when requirement validation fails."""
    pass

class MissionValidator:
    """
    Validator to enforce design requirements sanity checks for Multirotor UAVs.
    """
    SUPPORTED_MISSION_STRINGS = {
        "photography",
        "videography",
        "survey",
        "mapping",
        "inspection",
        "agriculture",
        "cargo delivery",
        "heavy lift",
        "search & rescue",
        "security",
        "infrastructure inspection",
        "emergency response",
        "research",
        "education",
        "indoor inspection",
    }

    def validate(self, requirements: RequirementModel) -> None:
        """
        Validates the RequirementModel parameters.
        Raises MissionValidationError if any sanity checks fail.
        """
        if not requirements:
            raise MissionValidationError("Requirements model cannot be None.")

        # 1. Validate payload weight
        if requirements.payload_weight_kg is None or requirements.payload_weight_kg <= 0.0:
            raise MissionValidationError(
                f"Payload weight must be positive. Obtained: {requirements.payload_weight_kg}"
            )
        if requirements.payload_weight_kg > 100.0:
            raise MissionValidationError(
                f"Payload weight exceeds physical capabilities of V4 sizing engine (max 100kg). Obtained: {requirements.payload_weight_kg}"
            )

        # 2. Validate target flight time
        if requirements.target_flight_time_min is None or requirements.target_flight_time_min <= 0.0:
            raise MissionValidationError(
                f"Target flight time must be positive. Obtained: {requirements.target_flight_time_min}"
            )
        if requirements.target_flight_time_min > 240.0:
            raise MissionValidationError(
                f"Target flight time exceeds physical battery capacity boundaries (max 240 min). Obtained: {requirements.target_flight_time_min}"
            )

        # 3. Validate target range
        if requirements.target_range_km is None or requirements.target_range_km <= 0.0:
            raise MissionValidationError(
                f"Target range must be positive. Obtained: {requirements.target_range_km}"
            )

        # 4. Validate cruise speed
        if requirements.cruise_speed_kmh is None or requirements.cruise_speed_kmh <= 0.0:
            raise MissionValidationError(
                f"Cruise speed must be positive. Obtained: {requirements.cruise_speed_kmh}"
            )

        # 5. Validate mission type
        mission_raw = requirements.mission_type
        mission_str = ""
        
        # Check if it is an enum or string
        if isinstance(mission_raw, MissionType):
            mission_str = mission_raw.value.lower()
        elif isinstance(mission_raw, str):
            mission_str = mission_raw.lower()
        else:
            raise MissionValidationError(f"Invalid mission type format: {type(mission_raw)}")

        # Check if in standard enum strings or specific custom strings
        is_supported = (
            mission_str in self.SUPPORTED_MISSION_STRINGS or 
            mission_str.upper() in MissionType.__members__
        )
        
        # Check metadata for custom multirotor mission definitions
        if not is_supported and mission_raw == MissionType.CUSTOM:
            custom_mission = requirements.metadata.get("multirotor_mission", "")
            if isinstance(custom_mission, str) and custom_mission.lower() in self.SUPPORTED_MISSION_STRINGS:
                is_supported = True

        if not is_supported:
            raise MissionValidationError(f"Unsupported mission type: {mission_raw}")

        # 6. Validate environment
        env_raw = requirements.environment
        if env_raw is not None and not isinstance(env_raw, (OperatingEnvironment, str)):
            raise MissionValidationError(f"Invalid environment type: {type(env_raw)}")
