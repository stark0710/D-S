"""
Fixed-Wing Center of Gravity (CG) Optimization Specification Model
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Any


@dataclass(slots=True)
class CGSpecification:
    """
    Standardized specification containing the balanced aircraft center of gravity,
    neutral point, static margin, component layout coordinates, and moment balance summaries.
    """
    # 3D Center of Gravity (m from nose)
    cg_position: Tuple[float, float, float]  # (cg_x, cg_y, cg_z)

    # Neutral point coordinate (m from nose)
    neutral_point: float

    # Sized stability margin
    static_margin: float

    # Component layout coordinates
    component_positions: Dict[str, Tuple[float, float, float]]

    # Sized mass moments (kg*m relative to nose)
    moment_summary: Dict[str, float]

    # Loading conditions envelopes
    cg_envelope: Dict[str, Tuple[float, float, float]]  # Empty, Operating, MTOW CGs

    # Optimization tracking
    optimization_score: float
    reasoning: str
