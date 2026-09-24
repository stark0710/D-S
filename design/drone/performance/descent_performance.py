"""
DescentPerformance Subsystem

Purpose:
    Defines the `DescentPerformance` class and `DescentPerformanceResult` dataclass for vertical descent safety evaluation.

Role in Architecture:
    `DescentPerformance` calculates safe maximum descent rate in m/s to prevent Vortex Ring State (VRS) aeromechanical instability.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DescentPerformanceResult:
    """
    Multirotor descent performance evaluation output model.

    Attributes:
        max_descent_rate_m_s (float): Recommended maximum controlled descent velocity in m/s (typically 3.0-5.0 m/s).
        vortex_ring_boundary_m_s (float): Calculated Vortex Ring State (VRS) induced velocity boundary in m/s.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    max_descent_rate_m_s: float
    vortex_ring_boundary_m_s: float
    metadata: dict[str, Any] = field(default_factory=dict)


class DescentPerformance:
    """
    Analysis service for safe vertical descent.

    Design Principles:
        - Single Responsibility Principle: Vertical descent rate and Vortex Ring State (VRS) boundary calculation only.
    """

    def analyze_descent(self, disk_loading_kg_m2: float) -> DescentPerformanceResult:
        """
        Calculates safe descent velocity to avoid Vortex Ring State (VRS).

        Args:
            disk_loading_kg_m2 (float): Disk loading in kg/m^2.

        Returns:
            DescentPerformanceResult: Computed descent performance output.
        """
        # Induced hover velocity v_i = sqrt((T/A) / (2 * rho))
        induced_v = (disk_loading_kg_m2 * 9.81 / (2.0 * 1.225)) ** 0.5
        vrs_boundary = round(induced_v * 0.8, 1)
        safe_descent_rate = min(5.0, max(2.5, round(vrs_boundary * 0.7, 1)))

        return DescentPerformanceResult(
            max_descent_rate_m_s=safe_descent_rate,
            vortex_ring_boundary_m_s=vrs_boundary
        )
