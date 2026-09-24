"""
Fixed-Wing Mass Properties Result Subsystem

Purpose:
    Defines the `MassResult` class representing the output of the mass properties analysis.

Role in Architecture:
    `MassResult` carries the calculated total masses, three-dimensional CG, principal moments of inertia,
    loading conditions, and static stability margins.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from backend.design.fixed_wing.mass_properties.weight_breakdown import WeightBreakdown
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass
from backend.design.fixed_wing.mass_properties.loading_conditions import LoadingCondition
from backend.design.fixed_wing.mass_properties.mass_analysis import MassAnalysis


@dataclass(slots=True)
class MassResult:
    """
    Consolidated output of the mass properties and center of gravity calculations.

    Attributes:
        weight_breakdown (WeightBreakdown): Sized weight fraction percentages.
        component_masses (List[ComponentMass]): Weight and spatial mapping of every subsystem.
        center_of_gravity (Tuple[float, float, float]): Sized longitudinal, lateral, and vertical coordinates (x, y, z).
        moments_of_inertia (Tuple[float, float, float]): Principal rolling, pitching, and yawing inertias (Ixx, Iyy, Izz).
        loading_conditions (List[LoadingCondition]): Loading envelopes (Empty, MTOW, etc).
        static_margin (float): Longitudinal static stability margin.
        mass_analysis (MassAnalysis): Weight efficiency and CG envelope suitability scores.
        engineering_notes (List[str]): Sizing rationale notes.
        recommendations (List[str]): Installation assembly guidelines.
        warnings (List[str]): Non-fatal warnings about weight budgets or stability margins.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    weight_breakdown: WeightBreakdown
    component_masses: List[ComponentMass]
    center_of_gravity: Tuple[float, float, float]
    moments_of_inertia: Tuple[float, float, float]
    loading_conditions: List[LoadingCondition]
    static_margin: float
    mass_analysis: MassAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Mass Result model.
"""
