"""
TradeoffAnalysis Subsystem

Purpose:
    Defines the `TradeoffAnalysis` class and `TradeoffAnalysisResult` dataclass for trade-off evaluation between optimization candidates.

Role in Architecture:
    `TradeoffAnalysis` compares baseline vs optimized candidates to quantify endurance gains, mass delta, and engineering trade-offs.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TradeoffAnalysisResult:
    """
    Multirotor optimization trade-off analysis output model.

    Attributes:
        endurance_gain_min (float): Flight endurance improvement in minutes.
        range_gain_km (float): Flight range improvement in km.
        mass_delta_kg (float): Total mass change in kg (negative means mass reduced).
        key_tradeoffs (list[str]): List of key engineering trade-offs.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    endurance_gain_min: float
    range_gain_km: float
    mass_delta_kg: float
    key_tradeoffs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TradeoffAnalysis:
    """
    Analysis service for candidate trade-off evaluation.

    Design Principles:
        - Single Responsibility Principle: Trade-off delta quantification between baseline and optimized candidates only.
    """

    def analyze_tradeoff(
        self,
        base_flight_time_min: float,
        base_range_km: float,
        base_mass_kg: float,
        opt_flight_time_min: float,
        opt_range_km: float,
        opt_mass_kg: float
    ) -> TradeoffAnalysisResult:
        """
        Quantifies trade-offs between baseline and optimized designs.

        Args:
            base_flight_time_min (float): Baseline flight time in min.
            base_range_km (float): Baseline range in km.
            base_mass_kg (float): Baseline mass in kg.
            opt_flight_time_min (float): Optimized flight time in min.
            opt_range_km (float): Optimized range in km.
            opt_mass_kg (float): Optimized mass in kg.

        Returns:
            TradeoffAnalysisResult: Computed trade-off analysis output.
        """
        e_gain = round(opt_flight_time_min - base_flight_time_min, 1)
        r_gain = round(opt_range_km - base_range_km, 1)
        m_delta = round(opt_mass_kg - base_mass_kg, 2)

        tradeoffs: list[str] = []
        if e_gain > 0:
            tradeoffs.append(f"Gained +{e_gain:.1f} minutes flight endurance.")
        if m_delta > 0:
            tradeoffs.append(f"AUW mass increased by +{m_delta:.2f} kg to achieve endurance targets.")
        elif m_delta < 0:
            tradeoffs.append(f"AUW mass reduced by {abs(m_delta):.2f} kg.")

        return TradeoffAnalysisResult(
            endurance_gain_min=e_gain,
            range_gain_km=r_gain,
            mass_delta_kg=m_delta,
            key_tradeoffs=tradeoffs
        )
