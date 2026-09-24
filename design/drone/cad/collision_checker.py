"""
CollisionChecker Subsystem

Purpose:
    Defines the `CollisionChecker` class for 3D bounding box interference detection.

Role in Architecture:
    `CollisionChecker` checks if any pair of 3D `CADComponent` bounding boxes overlap in space.
"""

from backend.design.drone.cad.cad_component import CADComponent


class CollisionChecker:
    """
    3D AABB bounding box collision detection service.

    Design Principles:
        - Single Responsibility Principle: 3D Axis-Aligned Bounding Box (AABB) intersection check only.
    """

    def check_collisions(self, components: list[CADComponent]) -> list[str]:
        """
        Detects 3D bounding box collisions between component pairs.

        Args:
            components (list[CADComponent]): List of CAD components.

        Returns:
            list[str]: List of detected collision error reports.
        """
        collisions: list[str] = []

        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                c1 = components[i]
                c2 = components[j]

                # Skip checking propeller to propeller if distinct arms
                if c1.category == "PROPELLER" and c2.category == "PROPELLER":
                    continue

                if self._aabb_intersect(c1, c2):
                    collisions.append(f"Collision detected between '{c1.name}' and '{c2.name}'.")

        return collisions

    def _aabb_intersect(self, c1: CADComponent, c2: CADComponent) -> bool:
        """Helper checking if two AABB bounding boxes intersect."""
        min1_x = c1.position_mm[0] - c1.bounding_box_mm[0] / 2.0
        max1_x = c1.position_mm[0] + c1.bounding_box_mm[0] / 2.0
        min1_y = c1.position_mm[1] - c1.bounding_box_mm[1] / 2.0
        max1_y = c1.position_mm[1] + c1.bounding_box_mm[1] / 2.0
        min1_z = c1.position_mm[2] - c1.bounding_box_mm[2] / 2.0
        max1_z = c1.position_mm[2] + c1.bounding_box_mm[2] / 2.0

        min2_x = c2.position_mm[0] - c2.bounding_box_mm[0] / 2.0
        max2_x = c2.position_mm[0] + c2.bounding_box_mm[0] / 2.0
        min2_y = c2.position_mm[1] - c2.bounding_box_mm[1] / 2.0
        max2_y = c2.position_mm[1] + c2.bounding_box_mm[1] / 2.0
        min2_z = c2.position_mm[2] - c2.bounding_box_mm[2] / 2.0
        max2_z = c2.position_mm[2] + c2.bounding_box_mm[2] / 2.0

        overlap_x = max1_x > min2_x and min1_x < max2_x
        overlap_y = max1_y > min2_y and min1_y < max2_y
        overlap_z = max1_z > min2_z and min1_z < max2_z

        return overlap_x and overlap_y and overlap_z
