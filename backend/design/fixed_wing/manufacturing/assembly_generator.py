"""
Fixed-Wing Assembly Documentation Generator Subsystem

Purpose:
    Defines the `AssemblyGenerator` class.

Role in Architecture:
    `AssemblyGenerator` generates step-by-step physical assembly instructions files.
"""

import os
from typing import List


class AssemblyGenerator:
    """
    Service compiling assembly step checklists.
    """

    def generate_assembly_instructions(
        self,
        output_dir: str,
        assembly_name: str,
    ) -> List[str]:
        """
        Generates assembly documentation markdown or text.

        Returns:
            List[str]: List of instruction file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{assembly_name}_assembly_guide.md")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Assembly Instructions for {assembly_name}\n\n")
            f.write("## Sequence Steps:\n")
            f.write("1. Mount flight controller and avionics onto battery tray in fuselage core.\n")
            f.write("2. Screw brushless motor firewall onto front fuselage bulkhead.\n")
            f.write("3. Slide left and right wing panels together using central carbon rod spar sleeve joints.\n")
            f.write("4. Torque wing mounts down onto fuselage floor plates using nylon M5 bolts.\n")
            f.write("5. Hook elevator and rudder control horns up to tail servos.\n")
            
        return [os.path.abspath(filepath)]
