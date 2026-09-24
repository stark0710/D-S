"""
VTOL Fuselage Profile Subsystem

Purpose:
    Defines the `FuselageProfile` class storing material densities
    and aerodynamic base drag targets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class FuselageProfile:
    """
    Standard references for structural fuselage calculations.

    Attributes:
        default_skin_thickness_mm (float): Sized carbon skin thickness in mm.
        composite_density_kg_m3 (float): Density of carbon fiber/epoxy composites in kg/m³.
        reference_drag_coefficient_cd0 (float): Baseline drag coefficient of the bare fuselage.
        metadata (Dict[str, Any]): Additional operational margins.
    """

    default_skin_thickness_mm: float = 1.2
    composite_density_kg_m3: float = 1550.0
    reference_drag_coefficient_cd0: float = 0.05
    metadata: Dict[str, Any] = field(default_factory=dict)
