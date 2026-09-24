"""
Fixed-Wing Manufacturing Result Subsystem

Purpose:
    Defines the `ManufacturingResult` class representing the production package data structures.

Role in Architecture:
    `ManufacturingResult` carries lists of bills of materials, cost estimates, drawings, and quality checklists.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(slots=True)
class ManufacturingResult:
    """
    Consolidated output of the manufacturing package generation workflow.

    Attributes:
        bill_of_materials (List[Dict[str, Any]]): Sized parts list with numbering, weights, and quantities.
        manufacturing_drawings (Dict[str, str]): Map of components to engineering drawing PDF paths.
        assembly_documents (List[str]): List of assembly sequence instruction files.
        exploded_views (List[str]): Paths to exploded visual renders.
        fabrication_files (Dict[str, str]): Map of process methods to export file paths (e.g. DXF, G-code).
        manufacturing_analysis (Dict[str, Any]): Nesting yields, time estimates, and complexity scores.
        manufacturing_cost (float): Total sized production unit cost estimate in USD.
        quality_checklist (List[str]): Quality assurance checklists.
        procurement_list (List[Dict[str, Any]]): Supplier, pricing, and sizing procurement entries.
        engineering_notes (List[str]): Sizing process plans.
        recommendations (List[str]): Sizing recommendations.
        warnings (List[str]): Sizing warnings.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    bill_of_materials: List[Dict[str, Any]]
    manufacturing_drawings: Dict[str, str]
    assembly_documents: List[str]
    exploded_views: List[str]
    fabrication_files: Dict[str, str]
    manufacturing_analysis: Dict[str, Any]
    manufacturing_cost: float
    quality_checklist: List[str]
    procurement_list: List[Dict[str, Any]]
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Manufacturing Result model.
"""
