"""
MissionCompliance Subsystem

Purpose:
    Defines the `MissionCompliance` class and `MissionComplianceResult` dataclass for mission objectives verification.

Role in Architecture:
    `MissionCompliance` evaluates whether the designed aircraft satisfies mission requirements (payload mass, flight endurance, range, cruise speed, wind tolerance).
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.mass_properties.mass_result import MassResult


@dataclass(slots=True)
class MissionComplianceResult:
    """
    Multirotor mission compliance verification output model.

    Attributes:
        compliant (bool): True if all mission objectives are fully satisfied.
        compliance_percentage (float): Percentage of mission requirements satisfied (0.0 to 100.0%).
        payload_satisfied (bool): True if payload capacity meets requirement.
        endurance_satisfied (bool): True if flight endurance meets requirement.
        range_satisfied (bool): True if flight range meets requirement.
        speed_satisfied (bool): True if cruise speed meets requirement.
        wind_satisfied (bool): True if wind tolerance meets requirement.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    compliant: bool
    compliance_percentage: float
    payload_satisfied: bool
    endurance_satisfied: bool
    range_satisfied: bool
    speed_satisfied: bool
    wind_satisfied: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class MissionCompliance:
    """
    Analysis service for mission objectives compliance.

    Design Principles:
        - Single Responsibility Principle: Mission requirement satisfaction evaluation only.
    """

    def verify_compliance(
        self,
        mission: DroneMissionProfile,
        performance_result: PerformanceResult,
        mass_result: MassResult
    ) -> MissionComplianceResult:
        """
        Verifies mission requirements compliance.

        Args:
            mission (DroneMissionProfile): Mission profile requirements.
            performance_result (PerformanceResult): Performance evaluation output.
            mass_result (MassResult): Mass properties output.

        Returns:
            MissionComplianceResult: Computed compliance output.
        """
        payload_ok = mass_result.payload_mass_kg >= (mission.payload_weight_kg * 0.95)
        endurance_ok = performance_result.flight_time_min >= (mission.target_hover_time_min + mission.target_cruise_time_min) * 0.90
        range_ok = performance_result.range_km >= (mission.target_range_km * 0.90)
        speed_ok = performance_result.cruise_speed_kmh >= (mission.cruise_speed_kmh * 0.90)
        wind_ok = performance_result.wind_analysis.max_wind_tolerance_m_s >= mission.max_wind_speed_m_s

        satisfied_count = sum([payload_ok, endurance_ok, range_ok, speed_ok, wind_ok])
        total_reqs = 5
        pct = (satisfied_count / total_reqs) * 100.0
        all_ok = satisfied_count == total_reqs

        return MissionComplianceResult(
            compliant=all_ok,
            compliance_percentage=round(pct, 1),
            payload_satisfied=payload_ok,
            endurance_satisfied=endurance_ok,
            range_satisfied=range_ok,
            speed_satisfied=speed_ok,
            wind_satisfied=wind_ok
        )
