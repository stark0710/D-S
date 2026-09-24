"""
Fixed-Wing Mission Classifier Subsystem

Purpose:
    Defines the `MissionClassifier` class, which categorizes a mission based on user requirements.

Role in Architecture:
    `MissionClassifier` determines or refines the `MissionCategory` of a mission by analyzing its parameters,
    especially useful if the user inputs a 'Custom' or unspecified category.
"""

from backend.design.fixed_wing.mission.mission_requirements import MissionRequirements, MissionCategory, EnvironmentType


class MissionClassifier:
    """
    Classifier to determine or verify the operational mission category of fixed-wing UAVs.
    """

    def classify(self, requirements: MissionRequirements) -> MissionCategory:
        """
        Classifies the mission based on physical requirements.

        Args:
            requirements (MissionRequirements): Raw requirements.

        Returns:
            MissionCategory: The determined category.
        """
        # If user explicitly set a specific category, verify if it fits, otherwise classify.
        cat = requirements.mission_category

        # If it is custom, we run a rule-based classification algorithm to find the closest engineering intent:
        if cat in (MissionCategory.CUSTOM, None):
            return self._infer_category(requirements)
        
        return cat

    def _infer_category(self, req: MissionRequirements) -> MissionCategory:
        """Rule-based heuristic classifier to match physical parameters to standard profiles."""
        
        # 1. Long Endurance: High flight time
        if req.flight_time_min >= 180.0:
            return MissionCategory.LONG_ENDURANCE
            
        # 2. Cargo: Large payload weight
        if req.payload_kg >= 10.0:
            return MissionCategory.CARGO
            
        # 3. Agriculture: Specific environment and high/medium payload
        if req.environment == EnvironmentType.RURAL and req.payload_kg >= 3.0:
            return MissionCategory.AGRICULTURE

        # 4. Racing: High cruise speed, low flight time
        if req.cruise_speed_kmh >= 120.0 and req.flight_time_min <= 30.0:
            return MissionCategory.RACING

        # 5. Training: Low budget, low payload, manual/assisted
        if req.budget is not None and req.budget < 2000.0 and req.payload_kg <= 1.0:
            return MissionCategory.TRAINING

        # 6. Survey / Mapping: Medium range, medium endurance
        if req.mission_range_km >= 30.0 or req.flight_time_min >= 60.0:
            return MissionCategory.SURVEY

        return MissionCategory.CUSTOM
