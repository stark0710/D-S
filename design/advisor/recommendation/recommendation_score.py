"""
RecommendationScore Enumeration Subsystem

Purpose:
    Defines the `RecommendationScore` enumeration representing qualitative rating bands for vehicle suitability.

Role in Architecture:
    `RecommendationScore` maps numeric suitability scores (0.0 to 1.0) into qualitative engineering categories
    (EXCELLENT, GOOD, ACCEPTABLE, POOR, UNSUITABLE) for explanation reporting.
"""

from enum import Enum


class RecommendationScore(str, Enum):
    """
    Qualitative recommendation suitability score rating.

    Members:
        EXCELLENT: Highly optimal category choice matching all primary mission targets (Score >= 0.85).
        GOOD: Strong category choice with minor non-critical trade-offs (0.70 <= Score < 0.85).
        ACCEPTABLE: Viable category choice with noticeable trade-offs (0.50 <= Score < 0.70).
        POOR: Sub-optimal category choice with major performance or operational drawbacks (0.30 <= Score < 0.50).
        UNSUITABLE: Unfeasible or unsafe category choice violating core physical bounds (Score < 0.30).
    """
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"
    UNSUITABLE = "UNSUITABLE"
