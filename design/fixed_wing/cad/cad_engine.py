"""
Fixed-Wing Parametric CAD Sizing Engine Subsystem

Purpose:
    Defines the `CADEngine` class, which serves as the orchestrator for the CAD Generation Framework.

Role in Architecture:
    `CADEngine` coordinates coordinate system alignments, lofts individual parts,
    compiles assemblies, handles format exports, and executes validation checks.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
import time
import os

from backend.design.fixed_wing.cad.cad_requirements import CADRequirements
from backend.design.fixed_wing.cad.cad_profile import CADProfile
from backend.design.fixed_wing.cad.cad_constraints import CADConstraints
from backend.design.fixed_wing.cad.cad_result import CADResult
from backend.design.fixed_wing.cad.cad_validator import CADValidator
from backend.design.fixed_wing.cad.cad_registry import CADStrategyRegistry, CADBackendRegistry
from backend.design.fixed_wing.cad.geometry_builder import GeometryBuilder
from backend.design.fixed_wing.cad.assembly_builder import AssemblyBuilder
from backend.design.fixed_wing.cad.coordinate_system import CoordinateSystem
from backend.design.fixed_wing.cad.reference_geometry import ReferenceGeometry
from backend.design.fixed_wing.cad.feature_tree import FeatureTree
from backend.design.fixed_wing.cad.parameter_mapper import ParameterMapper
from backend.design.fixed_wing.cad.wing_generator import WingGenerator
from backend.design.fixed_wing.cad.fuselage_generator import FuselageGenerator
from backend.design.fixed_wing.cad.tail_generator import TailGenerator
from backend.design.fixed_wing.cad.propulsion_generator import PropulsionGenerator
from backend.design.fixed_wing.cad.payload_generator import PayloadGenerator
from backend.design.fixed_wing.cad.fastener_generator import FastenerGenerator
from backend.design.fixed_wing.cad.cad_export import CADExport
from backend.design.fixed_wing.cad.cad_metadata import CADMetadata


class CADEngine:
    """
    Orchestrator driving the fixed-wing parametric CAD model generation workflow.
    """

    def __init__(
        self,
        validator: CADValidator | None = None,
        mapper: ParameterMapper | None = None,
        exporter: CADExport | None = None,
    ) -> None:
        self._validator = validator if validator else CADValidator()
        self._mapper = mapper if mapper else ParameterMapper()
        self._exporter = exporter if exporter else CADExport()

    def process_cad_generation(
        self,
        requirements: CADRequirements,
        profile: CADProfile | None = None,
    ) -> CADResult:
        """
        Generates and validates the parametric 3D CAD model.

        Args:
            requirements (CADRequirements): Sizing requirements context.
            profile (CADProfile | None): references and format limits.

        Returns:
            CADResult: 3D model data, assemblies, and export format links.
        """
        start_time = time.perf_counter()

        if profile is None:
            profile = CADProfile()

        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category
        wing_geom = requirements.wing_result.wing_geometry
        f_geom = requirements.fuselage_result.fuselage_geometry
        tail_geom = requirements.tail_result
        prop_res = requirements.propulsion_result
        pay_res = requirements.payload_result
        layout = requirements.configuration_result

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = CADStrategyRegistry.get(strategy_name)

        # target settings
        resolution, include_fasteners, simplify = strategy.get_generation_parameters()

        # Define constraints
        constraints = CADConstraints(
            allowed_export_formats=["STEP", "STL", "IGES", "GLTF", "OBJ", "PARASOLID"],
            min_clearance_mm=profile.clearance_tolerance_mm,
        )

        # 2. Map parameters
        cad_params = self._mapper.map_parameters(requirements)

        # 3. Initialize builders
        backend_api = CADBackendRegistry.get(profile.default_backend)
        builder = GeometryBuilder(profile.default_backend)
        assembly = AssemblyBuilder()
        feature_tree = FeatureTree()

        # 4. Position reference geometries
        ref_geom = ReferenceGeometry(
            symmetry_plane_normal=(0.0, 1.0, 0.0),
            thrust_axis=(1.0, 0.0, 0.0),
            datum_points=[
                ("Nose", (0.0, 0.0, 0.0)),
                ("Wing quarter-chord Aerodynamic Center", (wing_geom.quarter_chord_x_m, 0.0, 0.0)),
                ("Tail attachment", (f_geom.length_m - 0.12, 0.0, 0.05)),
            ],
        )

        # 5. Sizing and placement of parts
        parts: Dict[str, Any] = {}

        # Fuselage
        fuse_gen = FuselageGenerator(builder, feature_tree)
        parts["fuselage"] = fuse_gen.generate_fuselage(f_geom.length_m, f_geom.width_m, f_geom.height_m)
        fuse_cs = CoordinateSystem(origin=(0.0, 0.0, 0.0))
        assembly.position_part("fuselage", fuse_cs)

        # Wing
        wing_gen = WingGenerator(builder, feature_tree)
        parts["wing"] = wing_gen.generate_wing(
            wing_geom.span_m,
            wing_geom.root_chord_m,
            wing_geom.tip_chord_m,
            wing_geom.dihedral_angle_deg,
            wing_geom.taper_ratio,
        )
        wing_cs = CoordinateSystem(origin=(wing_geom.quarter_chord_x_m, 0.0, 0.0))
        assembly.position_part("wing", wing_cs)

        # Tail horizontal and vertical fins
        tail_gen = TailGenerator(builder, feature_tree)
        parts["tail"] = tail_gen.generate_tail(
            tail_geom.tail_configuration,
            tail_geom.horizontal_tail.span_m,
            tail_geom.vertical_tail.height_m,
        )
        tail_cs = CoordinateSystem(origin=(f_geom.length_m - 0.12, 0.0, 0.05))
        assembly.position_part("tail", tail_cs)

        # Propulsion
        prop_gen = PropulsionGenerator(builder, feature_tree)
        prop_diameter = prop_res.takeoff_analysis.metadata.get("prop_diameter_in", 10.0)
        is_pusher = "pusher" in layout.propulsion_configuration.lower()
        parts["propulsion"] = prop_gen.generate_propulsion(prop_diameter, is_pusher)
        prop_x = f_geom.length_m - 0.06 if is_pusher else 0.06
        prop_cs = CoordinateSystem(origin=(prop_x, 0.0, 0.0))
        assembly.position_part("propulsion", prop_cs)

        # Payload Compartment
        pay_gen = PayloadGenerator(builder, feature_tree)
        parts["payload"] = pay_gen.generate_payload(
            pay_res.payload_layout.compartment_length_m,
            pay_res.payload_layout.compartment_width_m,
            pay_res.payload_layout.compartment_height_m,
        )
        pay_cs = CoordinateSystem(origin=(pay_res.payload_layout.placement_x_m, 0.0, -0.05))
        assembly.position_part("payload", pay_cs)

        # Optional Fasteners
        if include_fasteners:
            fast_gen = FastenerGenerator(builder, feature_tree)
            parts["wing_bolts"] = fast_gen.generate_bolt("WingMountBolt", 5.0, 30.0)
            bolt_cs = CoordinateSystem(origin=(wing_geom.quarter_chord_x_m - 0.02, 0.02, 0.05))
            assembly.position_part("wing_bolts", bolt_cs)

        # 6. Sizing solids volume, masses, and bounding box offsets
        # Calculated volume: basic POD sum of components
        volume_m3 = (f_geom.length_m * f_geom.width_m * f_geom.height_m * 0.45) + (wing_geom.reference_area_m2 * 0.015)
        # Bounding box sizing
        bbox = (f_geom.length_m, wing_geom.span_m, max(f_geom.height_m, tail_geom.vertical_tail.height_m))

        # 7. Sizing CAD exports to disk
        export_dir = os.path.abspath(os.path.join(".", "exports", "fixed_wing_cad"))
        assembly_name = f"FixedWing_{category.name.upper()}_Assembly"
        
        exported_files = self._exporter.export_cad_model(
            output_dir=export_dir,
            assembly_name=assembly_name,
            formats=["STEP", "STL", "IGES", "GLTF"],
        )

        # 8. Compile diagnostics metadata
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000.0

        cad_metadata = CADMetadata(
            software_version="1.0.0",
            generating_backend=profile.default_backend,
            generation_time_ms=round(elapsed_ms, 1),
            bounding_box_dimensions=bbox,
            volume_m3=round(volume_m3, 5),
            mass_estimate_kg=requirements.mass_result.weight_breakdown.structural_weight_kg + requirements.mass_result.weight_breakdown.useful_load_kg,
            backend_metadata={
                "geometry_backend": profile.default_backend,
                "regeneration": "Successful",
                "mesh_resolution": resolution,
            },
        )

        # 9. Validate CAD geometries and exported paths
        warnings = self._validator.validate(
            volume_m3=volume_m3,
            bbox=bbox,
            parts=parts,
            exported_files=exported_files,
            allowed_formats=constraints.allowed_export_formats,
        )

        engineering_notes = [
            f"Parametric feature-based geometry created utilizing the '{profile.default_backend}' engine backend.",
            f"Chronological history tree built: {len(feature_tree.features)} modeling features.",
            f"Assembly successfully aligned: {len(assembly.placements)} sub-components positioned.",
            f"CAD volume: {volume_m3:.5f} m^3, mass: {cad_metadata.mass_estimate_kg:.2f} kg.",
            f"Bounding box: {bbox[0]:.2f}m length x {bbox[1]:.2f}m wingspan x {bbox[2]:.2f}m height.",
        ]

        recommendations = strategy.get_recommendations()

        # 10. Assemble CADResult
        return CADResult(
            cad_model=f"ParametricModelSolid({profile.default_backend})",
            assembly=assembly,
            parts=parts,
            feature_tree=feature_tree,
            reference_geometry=ref_geom,
            engineering_parameters=cad_params,
            exported_files=exported_files,
            cad_metadata=cad_metadata,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata={
                "strategy_applied": strategy.name,
                "backend_instance": backend_api,
            },
        )
