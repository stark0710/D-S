"""
AssemblyBuilder Subsystem

Purpose:
    Defines the `AssemblyBuilder` class for assembling individual `CADComponent` items into subassemblies and a Master Assembly.

Role in Architecture:
    `AssemblyBuilder` builds Frame, Propulsion, Electrical, Avionics, and Payload subassemblies, and links them into a `CADAssembly` hierarchy.
"""

from backend.design.drone.cad.cad_component import CADComponent
from backend.design.drone.cad.cad_assembly import CADAssembly


class AssemblyBuilder:
    """
    Subassembly and Master Assembly hierarchy construction service.

    Design Principles:
        - Single Responsibility Principle: Assembly tree node construction and total mass/bounding box calculation only.
    """

    def build_master_assembly(self, components: list[CADComponent]) -> CADAssembly:
        """
        Groups components into subassemblies and creates the master assembly tree.

        Args:
            components (list[CADComponent]): All 3D CAD components.

        Returns:
            CADAssembly: Root master assembly.
        """
        frame_sub = CADAssembly("Frame Subassembly", components=[c for c in components if c.category in ["FRAME", "LANDING_GEAR"]])
        prop_sub = CADAssembly("Propulsion Subassembly", components=[c for c in components if c.category in ["MOTOR", "PROPELLER"]])
        elec_sub = CADAssembly("Electrical Subassembly", components=[c for c in components if c.category in ["BATTERY", "ESC", "PDB"]])
        avionics_sub = CADAssembly("Avionics Subassembly", components=[c for c in components if c.category in ["FLIGHT_CONTROLLER", "GPS", "TELEMETRY", "RECEIVER"]])
        payload_sub = CADAssembly("Payload Subassembly", components=[c for c in components if c.category in ["PAYLOAD", "MOUNT"]])

        # Sum total mass
        total_m = sum(c.mass_g for c in components)

        # Calculate bounding box (max X, max Y, max Z span)
        max_x = max((abs(c.position_mm[0]) + c.bounding_box_mm[0] / 2.0) for c in components) * 2.0 if components else 500.0
        max_y = max((abs(c.position_mm[1]) + c.bounding_box_mm[1] / 2.0) for c in components) * 2.0 if components else 500.0
        max_z = max((abs(c.position_mm[2]) + c.bounding_box_mm[2] / 2.0) for c in components) * 2.0 if components else 300.0

        master = CADAssembly(
            assembly_name="Master Aircraft CAD Assembly",
            components=components,
            subassemblies=[frame_sub, prop_sub, elec_sub, avionics_sub, payload_sub],
            total_mass_g=round(total_m, 1),
            bounding_box_mm=(round(max_x, 1), round(max_y, 1), round(max_z, 1))
        )

        return master
