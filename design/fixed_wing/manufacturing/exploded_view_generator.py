"""
Fixed-Wing Exploded View Visual Generator Subsystem

Purpose:
    Defines the `ExplodedViewGenerator` class.

Role in Architecture:
    `ExplodedViewGenerator` creates references to visual positioning of parts.
"""

import os
from typing import List


class ExplodedViewGenerator:
    """
    Service generating exploded visual renders.
    """

    def generate_exploded_views(
        self,
        output_dir: str,
        assembly_name: str,
    ) -> List[str]:
        """
        Generates exploded assembly model formats.

        Returns:
            List[str]: List of exploded view file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{assembly_name}_exploded.obj")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Exploded Assembly Mesh file for {assembly_name}.\n")
            f.write("g wing_left\nv 0.0 1.5 0.2\n")
            f.write("g wing_right\nv 0.0 -1.5 0.2\n")
            f.write("g fuselage\nv 0.0 0.0 0.0\n")
            f.write("g tail\nv -1.38 0.0 0.1\n")
            
        return [os.path.abspath(filepath)]
