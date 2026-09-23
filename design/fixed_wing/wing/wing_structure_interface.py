"""
Fixed-Wing Wing Structure Interface Subsystem

Purpose:
    Defines the `WingStructureInterface` class representing the interface contract for structural weight
    and load evaluation.

Role in Architecture:
    `WingStructureInterface` establishes the contract between geometry sizing and structural weight calculations,
    allowing different material models or spar/rib layouts to be plugged in.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry


class WingStructureInterface(ABC):
    """
    Interface defining methods for structural evaluation and weight estimation of fixed-wing surfaces.
    """

    @abstractmethod
    def estimate_wing_weight_kg(
        self, geometry: WingGeometry, design_load_factor: float, structural_factor: float = 1.0
    ) -> float:
        """
        Estimates the structural weight of the wing in kilograms.

        Args:
            geometry (WingGeometry): Wing geometry dimensions.
            design_load_factor (float): Limit load factor (positive G limits, typically 3.0 to 6.0).
            structural_factor (float): Multiplier representing material density or construction style.

        Returns:
            float: Estimated weight of the wing structure in kg.
        """
        pass

    @abstractmethod
    def evaluate_structural_feasibility(
        self, geometry: WingGeometry, mtow_kg: float, design_load_factor: float
    ) -> Dict[str, Any]:
        """
        Evaluates structural feasibility indicators.

        Args:
            geometry (WingGeometry): Wing geometry dimensions.
            mtow_kg (float): Maximum Takeoff Weight of the aircraft in kg.
            design_load_factor (float): Ultimate design load factor.

        Returns:
            Dict[str, Any]: Dict containing keys for:
                - 'is_feasible' (bool)
                - 'structural_efficiency' (float)
                - 'max_bending_moment_nm' (float)
                - 'suggested_spar_thickness_mm' (float)
        """
        pass
