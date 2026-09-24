"""
ObjectiveFunction Subsystem

Purpose:
    Defines the `ObjectiveFunction` class and `ObjectiveScores` dataclass for multi-objective optimization scoring.

Role in Architecture:
    `ObjectiveFunction` evaluates candidate aircraft configurations across flight endurance, range, payload capacity,
    AUW mass minimization, power consumption minimization, reliability rating, and cost minimization objectives.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.mass_properties.mass_result import MassResult


@dataclass(slots=True)
class ObjectiveScores:
    """
    Multirotor optimization objective scores model.

    Attributes:
        endurance_score (float): Normalized flight endurance score (0-100).
        range_score (float): Normalized flight range score (0-100).
        payload_score (float): Normalized payload capacity score (0-100).
        mass_score (float): Normalized mass minimization score (0-100).
        efficiency_score (float): Normalized power consumption efficiency score (0-100).
        cost_score (float): Normalized cost minimization score (0-100).
        overall_objective_score (float): Composite weighted multi-objective score (0-100).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    endurance_score: float
    range_score: float
    payload_score: float
    mass_score: float
    efficiency_score: float
    cost_score: float
    overall_objective_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ObjectiveFunction:
    """
    Scoring service for multirotor optimization objectives.

    Design Principles:
        - Single Responsibility Principle: Objective metrics calculation and normalization only.
    """

    def evaluate_objectives(
        self,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        weights: dict[str, float] | None = None
    ) -> ObjectiveScores:
        """
        Evaluates objective scores for a candidate aircraft.

        Args:
            performance_result (PerformanceResult): Candidate performance result.
            mass_result (MassResult): Candidate mass properties result.
            weights (dict[str, float] | None): Optional objective weighting coefficients.

        Returns:
            ObjectiveScores: Computed objective scores model.
        """
        w = weights if weights else {
            "endurance": 0.30,
            "range": 0.20,
            "payload": 0.20,
            "mass": 0.10,
            "efficiency": 0.10,
            "cost": 0.10,
        }

        # Normalize metrics to 0-100 scale
        e_score = min(100.0, (performance_result.flight_time_min / 40.0) * 100.0)
        r_score = min(100.0, (performance_result.range_km / 30.0) * 100.0)
        p_score = min(100.0, (mass_result.payload_mass_kg / 5.0) * 100.0)
        m_score = max(0.0, 100.0 - (mass_result.total_mass_kg * 4.0))
        eff_score = min(100.0, performance_result.hover_performance.power_loading_g_w * 10.0)
        cost_score = 80.0  # Estimated baseline

        overall = (
            (e_score * w.get("endurance", 0.30)) +
            (r_score * w.get("range", 0.20)) +
            (p_score * w.get("payload", 0.20)) +
            (m_score * w.get("mass", 0.10)) +
            (eff_score * w.get("efficiency", 0.10)) +
            (cost_score * w.get("cost", 0.10))
        )

        return ObjectiveScores(
            endurance_score=round(e_score, 1),
            range_score=round(r_score, 1),
            payload_score=round(p_score, 1),
            mass_score=round(m_score, 1),
            efficiency_score=round(eff_score, 1),
            cost_score=round(cost_score, 1),
            overall_objective_score=round(overall, 1)
        )
