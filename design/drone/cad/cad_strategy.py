"""
CADStrategy Subsystem

Purpose:
    Defines the abstract `CADStrategy` interface and concrete multirotor CAD generation strategies.

Role in Architecture:
    `CADStrategy` implements the Strategy Pattern to build geometry, assembly hierarchy, collision checks,
    clearance checks, and CAD export payloads according to backend CAD platforms (Neutral CAD, FreeCAD, OpenVSP, SolidWorks, Fusion360, Onshape).
"""

from abc import ABC, abstractmethod
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.cad.cad_model import CADModel
from backend.design.drone.cad.geometry_builder import GeometryBuilder
from backend.design.drone.cad.assembly_builder import AssemblyBuilder
from backend.design.drone.cad.collision_checker import CollisionChecker
from backend.design.drone.cad.clearance_checker import ClearanceChecker
from backend.design.drone.cad.export_manager import ExportManager
from backend.design.drone.cad.cad_result import CADResult


class CADStrategy(ABC):
    """
    Abstract interface for multirotor CAD generation strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def generate_cad(
        self,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        export_format: str = "JSON_PARAMETRIC"
    ) -> CADResult:
        """
        Generates parametric 3D CAD model and assembly tree.

        Args:
            structure_result (FrameResult): Frame result.
            propulsion_result (PropulsionResult): Propulsion result.
            electrical_result (ElectricalResult): Electrical result.
            avionics_result (AvionicsResult): Avionics result.
            payload_result (PayloadResult): Payload result.
            export_format (str): Target export format string.

        Returns:
            CADResult: Completed CAD generation output summary.
        """
        pass


class NeutralCADStrategy(CADStrategy):
    """Standard neutral STEP/IGES/STL/JSON parametric CAD generation strategy."""

    @property
    def strategy_name(self) -> str:
        return "NeutralCADStrategy"

    def generate_cad(
        self,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        export_format: str = "JSON_PARAMETRIC"
    ) -> CADResult:
        geo_builder = GeometryBuilder()
        asm_builder = AssemblyBuilder()
        collision_engine = CollisionChecker()
        clearance_engine = ClearanceChecker()
        exporter = ExportManager()

        # Build geometry
        frame_comps = geo_builder.build_frame_geometry(structure_result)
        prop_comps = geo_builder.build_propulsion_geometry(propulsion_result, structure_result)
        sub_comps = geo_builder.build_subsystem_geometry(electrical_result, avionics_result, payload_result)

        all_comps = frame_comps + prop_comps + sub_comps

        # Build Master Assembly
        master_asm = asm_builder.build_master_assembly(all_comps)

        # Check collisions and clearances
        collisions = collision_engine.check_collisions(all_comps)
        clearances = clearance_engine.check_clearances(all_comps)

        # Build CAD model
        model = CADModel(
            model_name=f"Multirotor_{structure_result.selected_frame.frame_name}_CAD",
            assembly=master_asm,
            backend_strategy=self.strategy_name
        )

        # Export file payload
        files = exporter.export_assembly(master_asm, export_format)

        placements = [
            {"name": c.name, "category": c.category, "position_mm": c.position_mm, "rotation_deg": c.rotation_deg}
            for c in all_comps
        ]

        geo_analysis = {
            "total_components": len(all_comps),
            "master_bounding_box_mm": master_asm.bounding_box_mm,
            "total_mass_g": master_asm.total_mass_g
        }

        return CADResult(
            cad_model=model,
            assembly=master_asm,
            components=all_comps,
            placements=placements,
            geometry_analysis=geo_analysis,
            collision_report=collisions,
            clearance_report=clearances,
            generated_files=files,
            engineering_notes=f"Neutral CAD generation completed: {len(all_comps)} components assembled into master CAD tree."
        )


class FreeCADStrategy(CADStrategy):
    """FreeCAD parametric CAD generation strategy."""

    @property
    def strategy_name(self) -> str:
        return "FreeCADStrategy"

    def generate_cad(
        self,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        export_format: str = "FREECAD"
    ) -> CADResult:
        neutral = NeutralCADStrategy()
        res = neutral.generate_cad(structure_result, propulsion_result, electrical_result, avionics_result, payload_result, export_format)
        res.cad_model.backend_strategy = "FreeCADStrategy"
        res.engineering_notes = "FreeCAD parametric script export completed."
        return res
