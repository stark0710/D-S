"""
Fixed-Wing Airfoil Polar Analysis Subsystem

Purpose:
    Defines the `PolarData` class and the `PolarAnalysisService` class to evaluate polar coefficients.

Role in Architecture:
    Provides aerodynamic polar coefficients (CL, CD, L/D, CM) at cruise and finds the maximum lift-to-drag
    ratio (L/D_max) for the selected airfoil.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilRecord


@dataclass(slots=True)
class PolarData:
    """
    aerodynamic polar values under specific flow boundaries.

    Attributes:
        airfoil_name (str): Airfoil name.
        cruise_cl (float): Required lift coefficient at cruise.
        cruise_cd (float): Profile drag coefficient at cruise.
        cruise_l_d (float): Section lift-to-drag ratio at cruise.
        max_l_d (float): Maximum section lift-to-drag ratio (L/D_max).
        max_l_d_cl (float): Lift coefficient corresponding to L/D_max.
        max_lift_coeff (float): Maximum lift coefficient (Cl_max).
        stall_angle_deg (float): Section stall angle of attack in degrees.
        pitching_moment_c_m0 (float): Section zero-lift pitching moment coefficient.
        polar_curve (Dict[str, List[float]]): Array lists for 'alpha', 'cl', 'cd' for visualization.
    """

    airfoil_name: str
    cruise_cl: float
    cruise_cd: float
    cruise_l_d: float
    max_l_d: float
    max_l_d_cl: float
    max_lift_coeff: float
    stall_angle_deg: float
    pitching_moment_c_m0: float
    polar_curve: Dict[str, List[float]] = field(default_factory=dict)


class PolarAnalysisService:
    """
    Evaluator performing polar curves lookup, interpolation, and drag coefficient calculations.
    """

    def analyze_polar(self, airfoil: AirfoilRecord, target_cl: float, reynolds: float) -> PolarData:
        """
        Runs polar analyses on the airfoil at the designated Reynolds number.
        """
        # Cruise CD & L/D
        cruise_cd = airfoil.get_drag_coefficient(target_cl, reynolds)
        cruise_l_d = target_cl / max(0.0001, cruise_cd)

        # Find max L/D and search range
        max_l_d = 0.0
        max_l_d_cl = 0.0

        # Search across CL array to find maximum L/D ratio
        search_cl = [x * 0.02 for x in range(0, 80)]  # 0.0 to 1.6
        cl_max_re = airfoil.get_max_lift_coefficient(reynolds)
        
        curve_alpha: List[float] = []
        curve_cl: List[float] = []
        curve_cd: List[float] = []

        for cl in search_cl:
            if cl > cl_max_re:
                break
            
            cd = airfoil.get_drag_coefficient(cl, reynolds)
            l_d = cl / max(0.0001, cd)
            
            if l_d > max_l_d:
                max_l_d = l_d
                max_l_d_cl = cl

            # Approximate angle of attack: alpha = (Cl / 2pi) in radians, convert to degrees
            # plus zero-lift angle of attack (alpha0 approx -camber * 100)
            alpha_0 = -airfoil.camber_ratio * 100.0
            alpha = (cl / (2.0 * math.pi)) * (180.0 / math.pi) + alpha_0
            
            curve_alpha.append(round(alpha, 2))
            curve_cl.append(round(cl, 3))
            curve_cd.append(round(cd, 5))

        stall_angle = airfoil.get_stall_angle_deg(reynolds)

        return PolarData(
            airfoil_name=airfoil.name,
            cruise_cl=round(target_cl, 3),
            cruise_cd=round(cruise_cd, 5),
            cruise_l_d=round(cruise_l_d, 2),
            max_l_d=round(max_l_d, 2),
            max_l_d_cl=round(max_l_d_cl, 3),
            max_lift_coeff=cl_max_re,
            stall_angle_deg=stall_angle,
            pitching_moment_c_m0=airfoil.c_m0,
            polar_curve={
                "alpha_deg": curve_alpha,
                "cl": curve_cl,
                "cd": curve_cd,
            }
        )


# Import math at module level
import math
