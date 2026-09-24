"""
CADValidator Subsystem

Purpose:
    Defines the `CADValidator` class responsible for validating CAD generation outputs against constraints.

Role in Architecture:
    `CADValidator` checks collision reports, assembly bounding box limits, and component count bounds.
"""

from backend.design.drone.cad.cad_result import CADResult
from backend.design.drone.cad.cad_constraints import CADConstraints


class CADValidator:
    """
    Validator for multirotor CAD generation engineering outputs.

    Design Principles:
        - Single Responsibility Principle: CAD assembly completeness, collision-free verification, and envelope validation only.
    """

    def validate_cad(
        self,
        result: CADResult,
        constraints: CADConstraints
    ) -> list[str]:
        """
        Validates a CADResult against CADConstraints.

        Args:
            result (CADResult): Target CAD result object.
            constraints (CADConstraints): CAD constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        if len(result.collision_report) > 0:
            warnings.append(
                f"Assembly contains {len(result.collision_report)} detected 3D bounding box collision(s)."
            )

        bbox = result.assembly.bounding_box_mm
        max_bbox = constraints.max_bounding_box_mm
        if bbox[0] > max_bbox[0] or bbox[1] > max_bbox[1] or bbox[2] > max_bbox[2]:
            warnings.append(
                f"Master assembly bounding box ({bbox[0]}x{bbox[1]}x{bbox[2]}mm) exceeds envelope limit ({max_bbox[0]}x{max_bbox[1]}x{max_bbox[2]}mm)."
            )

        if len(result.components) > constraints.max_component_count:
            warnings.append(
                f"Component count ({len(result.components)}) exceeds maximum allowed limit ({constraints.max_component_count})."
            )

        return warnings
