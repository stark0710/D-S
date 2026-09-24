"""
Fixed-Wing Fuselage Result Subsystem

Purpose:
    Defines the `FuselageResult` class representing the output of the fuselage design and sizing process.

Role in Architecture:
    `FuselageResult` carries sized geometry, compartment dimensions, electronics locations,
    CG balances, firewall hardware, packing efficiency audits, and maintenance guidelines.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.internal_layout import InternalLayout
from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacement
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysis


@dataclass(slots=True)
class FuselageResult:
    """
    Consolidated output of the fuselage envelope sizing and internal integration workflow.

    Attributes:
        fuselage_geometry (FuselageGeometry): Sized outer dimensions and compartments.
        internal_layout (InternalLayout): positions of components and wiring paths.
        component_placement (ComponentPlacement): Mapped masses and calculated Center of Gravity.
        mounting_interfaces (MountingInterfaces): Wing joints, engine firewalls, and landing gear attachments.
        fuselage_analysis (FuselageAnalysis): Packaging volume, access, and aerodynamic drag audits.
        engineering_notes (List[str]): Sizing rationale and efficiency notes.
        recommendations (List[str]): Design and cooling recommendations.
        warnings (List[str]): Non-fatal warnings about packaging or thermal limits.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    fuselage_geometry: FuselageGeometry
    internal_layout: InternalLayout
    component_placement: ComponentPlacement
    mounting_interfaces: MountingInterfaces
    fuselage_analysis: FuselageAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
