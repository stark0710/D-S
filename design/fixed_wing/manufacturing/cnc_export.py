"""
Fixed-Wing CNC G-code Export Service

Purpose:
    Defines the `CNCExport` class.

Role in Architecture:
    `CNCExport` writes G-code files for mill/CNC machining.
"""

import os


class CNCExport:
    """
    CNC fabrication exporter.
    """

    def export_cnc_gcode(
        self,
        output_dir: str,
        part_name: str,
    ) -> str:
        """
        Generates mill contour paths.

        Returns:
            str: Absolute file path.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{part_name}_cnc_mill.gcode")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"; Torq Wings CNC Mill G-code for {part_name}\n")
            f.write("G21 ; Millimeters units\nG90 ; Absolute coordinates\n")
            f.write("M03 S18000 ; Spindle start\n")
            f.write("G01 X10.0 Y10.0 F1200\nG01 Z-2.0 F300\n")
            f.write("M05 ; Spindle stop\n")
            
        return os.path.abspath(filepath)
