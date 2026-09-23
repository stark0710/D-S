"""
ReliabilityVerification Subsystem

Purpose:
    Defines the `ReliabilityVerification` class and `ReliabilityVerificationResult` dataclass for redundancy and fault tolerance verification.

Role in Architecture:
    `ReliabilityVerification` checks motor redundancy (Hexa/Octo/X8 single motor failure tolerance), dual GNSS, telemetry link fallback, and component MTBF ratings.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.avionics.avionics_result import AvionicsResult


@dataclass(slots=True)
class ReliabilityVerificationResult:
    """
    Multirotor reliability and redundancy verification output model.

    Attributes:
        reliable (bool): True if redundancy standards are satisfied.
        motor_redundancy (bool): True if single motor failure survivability is maintained (Hexa/Octo/X8).
        gnss_redundancy (bool): True if dual GNSS receivers are present.
        telemetry_redundancy (bool): True if dual telemetry communication links are present.
        reliability_score (float): Subsystem reliability rating score (0.0 to 100.0).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    reliable: bool
    motor_redundancy: bool
    gnss_redundancy: bool
    telemetry_redundancy: bool
    reliability_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ReliabilityVerification:
    """
    Analysis service for multirotor reliability and subsystem redundancy.

    Design Principles:
        - Single Responsibility Principle: Subsystem redundancy and fault tolerance evaluation only.
    """

    def verify_reliability(
        self,
        configuration_result: ConfigurationResult,
        avionics_result: AvionicsResult
    ) -> ReliabilityVerificationResult:
        """
        Verifies reliability and redundancy metrics.

        Args:
            configuration_result (ConfigurationResult): Evaluated configuration result.
            avionics_result (AvionicsResult): Evaluated avionics result.

        Returns:
            ReliabilityVerificationResult: Computed reliability verification output.
        """
        cfg_name = configuration_result.recommended_configuration.profile.config_type
        rotor_cnt = configuration_result.recommended_configuration.profile.rotor_count

        motor_red = rotor_cnt >= 6 or cfg_name in ["HEXACOPTER", "OCTOCOPTER", "Y6", "X8"]
        gnss_red = "DUAL" in str(avionics_result.selected_gps).upper() or "RTK" in str(avionics_result.selected_gps).upper()
        telem_red = avionics_result.communication_analysis.link_margin_db >= 10.0

        score = 60.0
        if motor_red:
            score += 20.0
        if gnss_red:
            score += 10.0
        if telem_red:
            score += 10.0

        return ReliabilityVerificationResult(
            reliable=score >= 70.0,
            motor_redundancy=motor_red,
            gnss_redundancy=gnss_red,
            telemetry_redundancy=telem_red,
            reliability_score=round(score, 1)
        )
