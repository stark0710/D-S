"""
VTOL Fuselage Cooling System Subsystem

Purpose:
    Defines the `CoolingInlet` and `CoolingLayout` classes sizing NACA ducts
    and air flow pathways.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class CoolingInlet:
    """
    Sized cooling inlet duct on the fuselage surface.

    Attributes:
        name (str): Inlet type (e.g. Avionics NACA duct, Battery scoops).
        area_cm2 (float): Intake cross-section surface area.
        position_x_m (float): Distance from nose in meters.
        airflow_rate_m3_s (float): Calculated volumetric airflow rate at cruise.
    """

    name: str
    area_cm2: float
    position_x_m: float
    airflow_rate_m3_s: float


@dataclass(slots=True)
class CoolingLayout:
    """
    Consolidated cooling inlet maps.

    Attributes:
        inlets (List[CoolingInlet]): inlets list.
        has_active_cooling (bool): True if dynamic fan cooling is required for hover stages.
        estimated_cooling_effectiveness (float): thermal dissipation efficiency score.
        metadata (Dict[str, Any]): Internal heat sink properties.
    """

    inlets: List[CoolingInlet]
    has_active_cooling: bool
    estimated_cooling_effectiveness: float
    metadata: Dict[str, Any] = field(default_factory=dict)
