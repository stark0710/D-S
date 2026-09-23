"""
Fixed-Wing Airfoil Performance Map Subsystem

Purpose:
    Defines the `PerformanceMap` class and the `PerformanceMapService` class
    to generate performance grids across flight states.

Role in Architecture:
    Creates 2D maps of lift, drag, and L/D ratios over varying lift coefficients and Reynolds numbers.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilRecord


@dataclass(slots=True)
class PerformanceMap:
    """
    aerodynamic performance grid mapping lift coefficients and Reynolds numbers.

    Attributes:
        airfoil_name (str): The name of the mapped airfoil.
        reynolds_nodes (List[float]): Reynolds numbers grid points.
        cl_nodes (List[float]): Lift coefficients grid points.
        drag_grid (List[List[float]]): 2D grid of drag coefficients [Re_index][CL_index].
        l_d_grid (List[List[float]]): 2D grid of Lift-to-Drag ratios [Re_index][CL_index].
    """

    airfoil_name: str
    reynolds_nodes: List[float]
    cl_nodes: List[float]
    drag_grid: List[List[float]]
    l_d_grid: List[List[float]]


class PerformanceMapService:
    """
    Service building performance meshes across operational speeds and Reynolds bounds.
    """

    def generate_map(
        self,
        airfoil: AirfoilRecord,
        reynolds_min: float,
        reynolds_max: float,
        reynolds_steps: int = 5,
        cl_steps: int = 6,
    ) -> PerformanceMap:
        """
        Generates a 2D performance map grid.
        """
        # Node generation
        re_step_size = (reynolds_max - reynolds_min) / max(1, reynolds_steps - 1)
        reynolds_nodes = [reynolds_min + i * re_step_size for i in range(reynolds_steps)]

        # Cl nodes from 0.0 to 1.2
        cl_nodes = [0.0 + i * (1.2 / max(1, cl_steps - 1)) for i in range(cl_steps)]

        drag_grid: List[List[float]] = []
        l_d_grid: List[List[float]] = []

        for re in reynolds_nodes:
            drag_row: List[float] = []
            l_d_row: List[float] = []
            cl_max = airfoil.get_max_lift_coefficient(re)
            
            for cl in cl_nodes:
                if cl > cl_max:
                    # Beyond stall limit, store dummy or highly penalizing values
                    cd = airfoil.get_drag_coefficient(cl, re)
                    drag_row.append(round(cd, 5))
                    l_d_row.append(0.0)
                else:
                    cd = airfoil.get_drag_coefficient(cl, re)
                    l_d = cl / max(0.0001, cd)
                    drag_row.append(round(cd, 5))
                    l_d_row.append(round(l_d, 2))

            drag_grid.append(drag_row)
            l_d_grid.append(l_d_row)

        return PerformanceMap(
            airfoil_name=airfoil.name,
            reynolds_nodes=[round(re, 0) for re in reynolds_nodes],
            cl_nodes=[round(cl, 2) for cl in cl_nodes],
            drag_grid=drag_grid,
            l_d_grid=l_d_grid,
        )
