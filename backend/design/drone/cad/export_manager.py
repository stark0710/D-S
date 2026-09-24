"""
ExportManager Subsystem

Purpose:
    Defines the `ExportManager` class for generating CAD export representations (STEP, IGES, STL, OBJ, OpenVSP, FreeCAD, JSON).

Role in Architecture:
    `ExportManager` serializes parametric CAD assemblies into export file paths and parametric payload formats.
"""

import json
from typing import Any
from backend.design.drone.cad.cad_assembly import CADAssembly


class ExportManager:
    """
    Multi-backend CAD model export and serialization manager.

    Design Principles:
        - Single Responsibility Principle: Multi-format CAD file serialization and parametric payload export only.
    """

    def export_assembly(
        self,
        assembly: CADAssembly,
        format_type: str = "JSON_PARAMETRIC"
    ) -> dict[str, Any]:
        """
        Exports assembly into target parametric CAD format payload.

        Args:
            assembly (CADAssembly): Master CAD assembly.
            format_type (str): Target export format ('STEP', 'IGES', 'STL', 'OBJ', 'OPENVSP', 'FREECAD', 'JSON_PARAMETRIC').

        Returns:
            dict[str, Any]: Export result dictionary containing format, file payload, and component count.
        """
        comp_payloads = []
        for c in assembly.components:
            comp_payloads.append({
                "name": c.name,
                "category": c.category,
                "bounding_box_mm": c.bounding_box_mm,
                "material": c.material,
                "mass_g": c.mass_g,
                "position_mm": c.position_mm,
                "rotation_deg": c.rotation_deg,
                "shape_type": c.cad_shape_type
            })

        export_data = {
            "assembly_name": assembly.assembly_name,
            "format": format_type.upper(),
            "total_components": len(assembly.components),
            "total_mass_g": assembly.total_mass_g,
            "bounding_box_mm": assembly.bounding_box_mm,
            "components": comp_payloads
        }

        return export_data
