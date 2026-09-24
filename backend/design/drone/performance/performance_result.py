"""
PerformanceResult Subsystem

Purpose:
    Defines the `PerformanceResult` domain model representing output from the Drone Flight Performance Engineering Framework.

Role in Architecture:
    `PerformanceResult` encapsulates mission flight time in min, max hover time in min, range in km, cruise speed in kmh,
    maximum speed in kmh, `HoverPerformanceResult`, `ClimbPerformanceResult`, `DescentPerformanceResult`, `CruisePerformanceResult`,
    `StabilityAnalysisResult`, `WindAnalysisResult`, `EnergyAnalysisResult`, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.performance.hover_performance import HoverPerformanceResult
from backend.design.drone.performance.climb_performance import ClimbPerformanceResult
from backend.design.drone.performance.descent_performance import DescentPerformanceResult
from backend.design.drone.performance.cruise_performance import CruisePerformanceResult
from backend.design.drone.performance.stability_analysis import StabilityAnalysisResult
from backend.design.drone.performance.wind_analysis import WindAnalysisResult
from backend.design.drone.performance.energy_analysis import EnergyAnalysisResult


@dataclass(slots=True)
class PerformanceResult:
    """
    Multirotor flight performance engineering evaluation output summary.

    Attributes:
        flight_time_min (float): Estimated mission profile flight time in minutes.
        max_hover_time_min (float): Maximum hover flight time in minutes.
        range_km (float): Maximum operational flight range in km.
        cruise_speed_kmh (float): Optimal cruise speed in km/h.
        maximum_speed_kmh (float): Maximum horizontal speed in km/h.
        hover_performance (HoverPerformanceResult): Hover performance output.
        climb_performance (ClimbPerformanceResult): Climb performance output.
        descent_performance (DescentPerformanceResult): Descent performance output.
        cruise_performance (CruisePerformanceResult): Cruise performance output.
        stability_analysis (StabilityAnalysisResult): Control authority stability output.
        wind_analysis (WindAnalysisResult): Wind tolerance capability output.
        energy_analysis (EnergyAnalysisResult): Battery energy rate and reserve output.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during performance evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    flight_time_min: float
    max_hover_time_min: float
    range_km: float
    cruise_speed_kmh: float
    maximum_speed_kmh: float
    hover_performance: HoverPerformanceResult
    climb_performance: ClimbPerformanceResult
    descent_performance: DescentPerformanceResult
    cruise_performance: CruisePerformanceResult
    stability_analysis: StabilityAnalysisResult
    wind_analysis: WindAnalysisResult
    energy_analysis: EnergyAnalysisResult
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
