"""
DroneMissionEngine Subsystem

Purpose:
    Defines the `DroneMissionEngine` class, which serves as the public entry point for multirotor mission engineering.

Role in Architecture:
    `DroneMissionEngine` converts a `DroneMissionProfile` into multirotor engineering requirements and constraints,
    validates mission parameters, and returns a `DroneMissionResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.mission.drone_mission_requirements import DroneMissionRequirements
from backend.design.drone.mission.drone_mission_constraints import DroneMissionConstraints
from backend.design.drone.mission.drone_mission_result import DroneMissionResult
from backend.design.drone.mission.drone_mission_validator import DroneMissionValidator
from backend.design.drone.mission.drone_mission_analysis import DroneMissionAnalysis


class DroneMissionEngine:
    """
    Public entry point service for multirotor mission engineering decomposition.

    Design Principles:
        - Single Responsibility Principle: Multirotor mission requirement and constraint decomposition only.
        - Dependency Injection: Injects `DroneMissionValidator` and `DroneMissionAnalysis` collaborators.
        - Non-Calculation: Does not perform component selection, compatibility checks, or trade-off optimizations.
    """

    def __init__(
        self,
        validator: DroneMissionValidator | None = None,
        analysis: DroneMissionAnalysis | None = None
    ) -> None:
        """
        Initializes the DroneMissionEngine.

        Args:
            validator (DroneMissionValidator | None): Injected validator collaborator.
            analysis (DroneMissionAnalysis | None): Injected analysis collaborator.
        """
        self._validator: DroneMissionValidator = validator if validator else DroneMissionValidator()
        self._analysis: DroneMissionAnalysis = analysis if analysis else DroneMissionAnalysis()

    def process_mission(self, profile: DroneMissionProfile) -> DroneMissionResult:
        """
        Processes a DroneMissionProfile and decomposes it into multirotor requirements and constraints.

        Args:
            profile (DroneMissionProfile): Input multirotor mission profile.

        Returns:
            DroneMissionResult: Decomposed multirotor mission engineering output summary.
        """
        warnings = self._validator.validate_mission(profile)
        requirements = self._analysis.derive_requirements(profile)
        constraints = self._analysis.derive_constraints(profile, requirements)

        return DroneMissionResult(
            mission_profile=profile,
            engineering_requirements=requirements,
            constraints=constraints,
            warnings=warnings,
            metadata={"decomposed_by": "DroneMissionEngine"}
        )
