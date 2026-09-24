"""
Fixed-Wing CAD Sizing Strategy Subsystem

Purpose:
    Defines the `CADStrategy` base class and concrete selection strategies for 3D model features.

Role in Architecture:
    The strategy pattern isolates resolution parameters, fastener inclusion flags, and warnings.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class CADStrategy(ABC):
    """
    Abstract base class for all fixed-wing CAD strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        """
        Returns strategy settings: (mesh_resolution, include_fasteners, simplify_for_fea).
        """
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates CAD usage recommendations."""
        pass


class BaseCADStrategy(CADStrategy):
    """
    Common base implementation of CADStrategy.
    """

    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        return "Medium", True, False

    def get_recommendations(self) -> List[str]:
        return [
            "Use STEP files for importing into parametric CAD programs like SolidWorks.",
            "Use STL files for mesh-based workflows or basic visual renders.",
        ]


class RapidPrototypeCADStrategy(BaseCADStrategy):
    """Strategy optimized for quick 3D printing and fast generation."""

    @property
    def name(self) -> str:
        return "Rapid Prototype"

    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        return "Low", False, False  # low resolution, skip fasteners

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Export to STL format for rapid 3D printing slicing software.",
        ])
        return recs


class ManufacturingCADStrategy(BaseCADStrategy):
    """Strategy optimized for CNC machining and laser-cutting assemblies."""

    @property
    def name(self) -> str:
        return "Manufacturing"

    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        return "High", True, False  # high detail, full fasteners

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Verify drill hole tolerances on motor mounts against motor bolts spec sheets before manufacturing.",
        ])
        return recs


class SimulationCADStrategy(BaseCADStrategy):
    """Strategy optimized for CFD (aerodynamics) and FEA (structural mesh)."""

    @property
    def name(self) -> str:
        return "Simulation"

    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        return "Medium", False, True  # medium resolution, skip fasteners, simplify geometry

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "CFD geometry is simplified. Bounding surfaces are clean without screws/bolts to ease mesh generation.",
        ])
        return recs


class LightweightCADStrategy(BaseCADStrategy):
    """Strategy optimized for lightweight skeletal outlines and fast visual loads."""

    @property
    def name(self) -> str:
        return "Lightweight"

    def get_generation_parameters(self) -> Tuple[str, bool, bool]:
        return "Low", False, True


class ResearchCADStrategy(BaseCADStrategy):
    """Strategy optimized for custom code checks."""

    @property
    def name(self) -> str:
        return "Research"


class BalancedCADStrategy(BaseCADStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
"""
Fixed-Wing CAD Strategy models.
"""
