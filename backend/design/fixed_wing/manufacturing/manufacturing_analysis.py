"""
Fixed-Wing Manufacturing Sizing Analysis Subsystem

Purpose:
    Defines the `ManufacturingAnalysis` class.

Role in Architecture:
    `ManufacturingAnalysis` holds nesting yields, build times, and complexity scores.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(slots=True)
class ManufacturingAnalysis:
    """
    Manufacturing complexity and process planning analytics.

    Attributes:
        manufacturability_rating (str): Sizing rating ("Easy", "Moderate", "Hard").
        total_build_time_hours (float): Total manual and machine build time estimate.
        nesting_layout_yield_pct (float): nesting sheet utilization percent.
        quality_risk_factors (List[str]): List of identified quality risks.
        process_metadata (Dict[str, Any]): Intermediate calculations logs.
    """

    manufacturability_rating: str
    total_build_time_hours: float
    nesting_layout_yield_pct: float
    quality_risk_factors: List[str] = field(default_factory=list)
    process_metadata: Dict[str, Any] = field(default_factory=dict)
