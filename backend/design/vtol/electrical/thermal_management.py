"""
VTOL Electrical Thermal Management Subsystem

Purpose:
    Defines the `ThermalAnalysis` class estimating battery pack heating rates.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ThermalAnalysis:
    """
    Sized thermal loads of the battery pack.

    Attributes:
        hover_heat_generation_w (float): Power dissipated as heat ($I^2 R$) during hover.
        cruise_heat_generation_w (float): Power dissipated as heat during cruise.
        estimated_pack_temp_c (float): Sized continuous temperature under hover load.
        cooling_method_required (str): Required cooling style (e.g. Passive air ducts, Active cooling fan).
        metadata (Dict[str, Any]): Internal specific heats details.
    """

    hover_heat_generation_w: float
    cruise_heat_generation_w: float
    estimated_pack_temp_c: float
    cooling_method_required: str
    metadata: Dict[str, Any] = field(default_factory=dict)
