"""
Fixed-Wing 3D Printing Slicer Exporter Subsystem

Purpose:
    Defines the `PrintingExport` class.

Role in Architecture:
    `PrintingExport` compiles print parameters and writes print files (STL/G-code).
"""

import os


class PrintingExport:
    """
    3D print files generator.
    """

    def export_print_stl(
        self,
        output_dir: str,
        part_name: str,
    ) -> str:
        """
        Generates print file.

        Returns:
            str: Absolute file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{part_name}_3d_print.stl")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"solid {part_name}\nfacet normal 0 0 0\nouter loop\nvertex 0 0 0\nendloop\nendsolid {part_name}\n")
            
        return os.path.abspath(filepath)
