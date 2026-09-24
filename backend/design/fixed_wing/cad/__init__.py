"""
Fixed-Wing CAD Generation Framework Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing CAD Sizing Framework.
"""

from backend.design.fixed_wing.cad.cad_requirements import CADRequirements
from backend.design.fixed_wing.cad.cad_profile import CADProfile
from backend.design.fixed_wing.cad.cad_constraints import CADConstraints
from backend.design.fixed_wing.cad.cad_result import CADResult
from backend.design.fixed_wing.cad.cad_validator import CADValidator, CADValidationError
from backend.design.fixed_wing.cad.cad_metadata import CADMetadata
from backend.design.fixed_wing.cad.coordinate_system import CoordinateSystem
from backend.design.fixed_wing.cad.reference_geometry import ReferenceGeometry
from backend.design.fixed_wing.cad.feature_tree import FeatureTree
from backend.design.fixed_wing.cad.parameter_mapper import ParameterMapper
from backend.design.fixed_wing.cad.geometry_builder import GeometryBuilder
from backend.design.fixed_wing.cad.assembly_builder import AssemblyBuilder
from backend.design.fixed_wing.cad.part_generator import PartGenerator
from backend.design.fixed_wing.cad.wing_generator import WingGenerator
from backend.design.fixed_wing.cad.fuselage_generator import FuselageGenerator
from backend.design.fixed_wing.cad.tail_generator import TailGenerator
from backend.design.fixed_wing.cad.propulsion_generator import PropulsionGenerator
from backend.design.fixed_wing.cad.payload_generator import PayloadGenerator
from backend.design.fixed_wing.cad.fastener_generator import FastenerGenerator
from backend.design.fixed_wing.cad.cad_export import CADExport
from backend.design.fixed_wing.cad.cad_strategy import CADStrategy
from backend.design.fixed_wing.cad.cad_registry import CADStrategyRegistry, CADBackendRegistry
from backend.design.fixed_wing.cad.cad_engine import CADEngine

__all__ = [
    "CADRequirements",
    "CADProfile",
    "CADConstraints",
    "CADResult",
    "CADValidator",
    "CADValidationError",
    "CADMetadata",
    "CoordinateSystem",
    "ReferenceGeometry",
    "FeatureTree",
    "ParameterMapper",
    "GeometryBuilder",
    "AssemblyBuilder",
    "PartGenerator",
    "WingGenerator",
    "FuselageGenerator",
    "TailGenerator",
    "PropulsionGenerator",
    "PayloadGenerator",
    "FastenerGenerator",
    "CADExport",
    "CADStrategy",
    "CADStrategyRegistry",
    "CADBackendRegistry",
    "CADEngine",
]
