"""
Fixed-Wing Laser Cutting Exporter Subsystem

Purpose:
    Defines the `LaserExport` class.

Role in Architecture:
    `LaserExport` writes DXF laser cutter vector profiles.
"""

import os


class LaserExport:
    """
    Laser cutter profile exporter.
    """

    def export_laser_dxf(
        self,
        output_dir: str,
        part_name: str,
    ) -> str:
        """
        Generates laser contour DXF coordinates.

        Returns:
            str: Absolute file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{part_name}_laser_cut.dxf")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("0\nSECTION\n2\nHEADER\n")
            f.write("0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")
            # Circle profile for holes
            f.write("0\nCIRCLE\n8\nLASER_CUT_LAYER\n10\n0.0\n20\n0.0\n40\n5.0\n")
            f.write("0\nENDSEC\n0\nEOF\n")
            
        return os.path.abspath(filepath)
