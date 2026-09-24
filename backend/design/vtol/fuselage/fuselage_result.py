"""
VTOL Fuselage Sizing Result Subsystem

Purpose:
    Defines the consolidated `FuselageResult` dataclass outputted by the fuselage stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.vtol.fuselage.fuselage_structure import FuselageStructure
from backend.design.vtol.fuselage.internal_layout import InternalLayout
from backend.design.vtol.fuselage.compartment_layout import CompartmentLayout
from backend.design.vtol.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.vtol.fuselage.cooling_layout import CoolingLayout
from backend.design.vtol.fuselage.fuselage_analysis import FuselageAnalysis


@dataclass(slots=True)
class FuselageResult:
    """
    Consolidated fuselage sizing package detailing structural layouts and packing.

    Attributes:
        fuselage_geometry (FuselageGeometry): Sized length, width, height, and volumes.
        structural_layout (FuselageStructure): Shell materials, weights, and reinforcements.
        internal_layout (InternalLayout): placements list and CG calculations.
        compartment_layout (CompartmentLayout): Sized compartment allocations.
        mounting_interfaces (MountingInterfaces): hardpoint coordinates.
        cooling_layout (CoolingLayout): Cooling ducts coordinates.
        engineering_analysis (FuselageAnalysis): Performance metrics.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Downstream recommendations.
        warnings (List[str]): Safety/clearance warnings.
        metadata (Dict[str, Any]): execution timestamps and versions.
    """

    fuselage_geometry: FuselageGeometry
    structural_layout: FuselageStructure
    internal_layout: InternalLayout
    compartment_layout: CompartmentLayout
    mounting_interfaces: MountingInterfaces
    cooling_layout: CoolingLayout
    engineering_analysis: FuselageAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
