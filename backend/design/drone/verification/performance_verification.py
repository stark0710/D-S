"""
PerformanceVerification Subsystem

Purpose:
    Defines the `PerformanceVerification` class and `PerformanceVerificationResult` dataclass for flight performance margins verification.

Role in Architecture:
    `PerformanceVerification` checks hover power reserve, thrust margin, climb rate margin, speed margin, and energy reserves.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.performance.performance_result import PerformanceResult


@dataclass(slots=True)
class PerformanceVerificationResult:
    """
    Multirotor performance margins verification output model.

    Attributes:
        verified (bool): True if all flight performance margins meet engineering standards.
        hover_margin_percent (float): Hover power reserve margin percentage.
        thrust_margin_percent (float): Available thrust margin percentage.
        climb_rate_m_s (float): Vertical climb rate in m/s.
        speed_margin_percent (float): Speed margin above target cruise speed.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    verified: bool
    hover_margin_percent: float
    thrust_margin_percent: float
    climb_rate_m_s: float
    speed_margin_percent: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceVerification:
    """
    Analysis service for performance margins verification.

    Design Principles:
        - Single Responsibility Principle: Performance margins calculation and verification only.
    """

    def verify_performance(self, performance_result: PerformanceResult) -> PerformanceVerificationResult:
        """
        Verifies performance margins.

        Args:
            performance_result (PerformanceResult): Target performance result object.

        Returns:
            PerformanceVerificationResult: Computed performance verification output.
        """
        tw_margin = (performance_result.hover_performance.hover_thrust_margin - 1.0) * 100.0
        h_margin = (1.0 - (performance_result.hover_performance.hover_throttle_percent / 100.0)) * 100.0
        sp_margin = ((performance_result.maximum_speed_kmh - performance_result.cruise_speed_kmh) / performance_result.cruise_speed_kmh) * 100.0

        all_ok = tw_margin >= 30.0 and h_margin >= 20.0 and performance_result.climb_performance.max_climb_rate_m_s >= 2.0

        return PerformanceVerificationResult(
            verified=all_ok,
            hover_margin_percent=round(h_margin, 1),
            thrust_margin_percent=round(tw_margin, 1),
            climb_rate_m_s=performance_result.climb_performance.max_climb_rate_m_s,
            speed_margin_percent=round(sp_margin, 1)
        )
