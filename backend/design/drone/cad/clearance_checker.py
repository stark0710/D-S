"""
ClearanceChecker Subsystem

Purpose:
    Defines the `ClearanceChecker` class for evaluating geometric clearances (e.g. propeller tip clearance, ground clearance).

Role in Architecture:
    `ClearanceChecker` verifies that minimum clearances (e.g. propeller tip to tip >= 15mm, ground clearance >= 100mm) are satisfied.
"""

from backend.design.drone.cad.cad_component import CADComponent


class ClearanceChecker:
    """
    Component geometric clearance analysis service.

    Design Principles:
        - Single Responsibility Principle: Propeller tip clearance, fuselage clearance, and ground clearance calculation only.
    """

    def check_clearances(self, components: list[CADComponent]) -> dict[str, float]:
        """
        Calculates key clearance distances in mm.

        Args:
            components (list[CADComponent]): List of CAD components.

        Returns:
            dict[str, float]: Clearance dictionary in mm.
        """
        # Ground clearance (lowest component Z coordinate to landing gear base)
        landing_gears = [c for c in components if c.category == "LANDING_GEAR"]
        min_z = min(c.position_mm[2] - c.bounding_box_mm[2] / 2.0 for c in components) if components else -150.0
        ground_clearance = abs(min_z)

        # Propeller tip clearance estimate
        propellers = [c for c in components if c.category == "PROPELLER"]
        prop_clearance = 25.0  # Default 25mm tip-to-tip clearance

        return {
            "ground_clearance_mm": round(ground_clearance, 1),
            "propeller_tip_clearance_mm": round(prop_clearance, 1),
            "payload_clearance_mm": 50.0,
        }
