"""
Fixed-Wing 2D Engineering Drawing Generator Subsystem

Purpose:
    Defines the `DrawingGenerator` class.

Role in Architecture:
    `DrawingGenerator` simulates compiling PDF dimension sheets for parts.
"""

import os
from typing import Dict, List


class DrawingGenerator:
    """
    Service generating PDF engineering drawing files.
    """

    def generate_drawings(
        self,
        output_dir: str,
        components: List[str],
        sheet_size: str,
    ) -> Dict[str, str]:
        """
        Simulates drawing generation.

        Returns:
            Dict[str, str]: Map of component name to drawing file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        drawings: Dict[str, str] = {}

        for comp in components:
            filepath = os.path.join(output_dir, f"{comp}_2d_drawing.pdf")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"%PDF-1.4\n% Torq Wings Sized Engineering Drawing for component: {comp} on {sheet_size} sheets.\n")
            drawings[comp] = os.path.abspath(filepath)

        return drawings
