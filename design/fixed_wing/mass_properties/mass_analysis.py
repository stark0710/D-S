"""
Fixed-Wing Mass Analysis Subsystem

Purpose:
    Defines the `MassAnalysis` class holding CG suitability scores and weight efficiency.

Role in Architecture:
    `MassAnalysis` aggregates efficiency coefficients and textual summaries for reports.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MassAnalysis:
    """
    aerodynamic, structural, and weight efficiency score metrics.

    Attributes:
        weight_distribution_score (float): Sized rating for airframe loading layout (0.0 to 100.0).
        cg_envelope_suitability_score (float): Sized rating for CG travel limits (0.0 to 100.0).
        static_margin_suitability_score (float): Rating for stability margins.
        structural_load_index (float): structural safety multiplier.
        weight_efficiency_ratio (float): Ratio of useful load to MTOW.
        analysis_summary (str): textual evaluation summary.
    """

    weight_distribution_score: float
    cg_envelope_suitability_score: float
    static_margin_suitability_score: float
    structural_load_index: float
    weight_efficiency_ratio: float
    analysis_summary: str
