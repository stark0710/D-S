"""
Fixed-Wing Glide Performance Analysis Subsystem

Purpose:
    Defines the `GlideAnalysis` class.

Role in Architecture:
    `GlideAnalysis` holds glide ratios (L/D) and unpowered descent glide angles.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class GlideAnalysis:
    """
    Unpowered gliding performance metrics.

    Attributes:
        glide_ratio (float): Gliding range multiplier (equivalent to L/D).
        minimum_glide_angle_deg (float): Shallowest descent path angle.
        sink_rate_min_m_s (float): Minimum sink rate during unpowered glide.
        metadata (Dict[str, Any]): Aerodynamic speeds.
    """

    glide_ratio: float
    minimum_glide_angle_deg: float
    sink_rate_min_m_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
